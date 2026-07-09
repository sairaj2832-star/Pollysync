import { useRef, useEffect } from "react";

const VS = `attribute vec2 a_position;
void main() {
  gl_Position = vec4(a_position, 0.0, 1.0);
}`;

const SHADERS = {
  dark: `precision highp float;
uniform float u_time;
uniform vec2 u_resolution;
void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    float noise1 = sin(uv.x * 2.5 + u_time * 0.4) * 0.5 + 0.5;
    float noise2 = sin(uv.y * 3.5 - u_time * 0.2) * 0.5 + 0.5;
    vec3 emerald = vec3(0.06, 0.72, 0.50);
    vec3 slate950 = vec3(0.06, 0.09, 0.16);
    vec3 color = mix(slate950, emerald * 0.3, noise1 * 0.4);
    color = mix(color, emerald * 0.1, noise2 * 0.2);
    float pulse = sin(u_time * 0.5) * 0.05 + 0.95;
    gl_FragColor = vec4(color * pulse, 1.0);
}`,
  light: `precision highp float;
uniform float u_time;
uniform vec2 u_resolution;
void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    float noise1 = sin(uv.x * 3.0 + u_time * 0.5) * 0.5 + 0.5;
    float noise2 = sin(uv.y * 2.0 - u_time * 0.3) * 0.5 + 0.5;
    vec3 emerald = vec3(0.06, 0.72, 0.50);
    vec3 amber = vec3(0.96, 0.62, 0.04);
    vec3 surface = vec3(0.98, 0.98, 0.97);
    vec3 color = mix(surface, emerald, noise1 * 0.2);
    color = mix(color, amber, noise2 * 0.15);
    float vignette = 1.0 - length(uv - 0.5) * 0.5;
    gl_FragColor = vec4(color * vignette, 1.0);
}`,
};

export default function ShaderBackground({ variant = "dark", className = "" }) {
  const canvasRef = useRef(null);
  const animRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
    if (!gl) return;

    function syncSize() {
      const w = canvas.clientWidth || 1280;
      const h = canvas.clientHeight || 720;
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }
    }

    const ro = new ResizeObserver(syncSize);
    ro.observe(canvas);
    syncSize();

    const fs = SHADERS[variant] || SHADERS.dark;

    function compile(type, src) {
      const s = gl.createShader(type);
      gl.shaderSource(s, src);
      gl.compileShader(s);
      return s;
    }

    const prog = gl.createProgram();
    gl.attachShader(prog, compile(gl.VERTEX_SHADER, VS));
    gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, fs));
    gl.linkProgram(prog);
    gl.useProgram(prog);

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);

    const pos = gl.getAttribLocation(prog, "a_position");
    gl.enableVertexAttribArray(pos);
    gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);

    const uTime = gl.getUniformLocation(prog, "u_time");
    const uRes = gl.getUniformLocation(prog, "u_resolution");

    let mouse = { x: canvas.width / 2, y: canvas.height / 2 };
    const uMouse = gl.getUniformLocation(prog, "u_mouse");
    function onMouse(e) {
      const rect = canvas.getBoundingClientRect();
      if (rect.width && rect.height) {
        const nx = (e.clientX - rect.left) / rect.width;
        const ny = 1.0 - (e.clientY - rect.top) / rect.height;
        mouse.x = nx * canvas.width;
        mouse.y = ny * canvas.height;
      }
    }
    window.addEventListener("mousemove", onMouse);

    function render(t) {
      syncSize();
      gl.viewport(0, 0, canvas.width, canvas.height);
      if (uTime) gl.uniform1f(uTime, t * 0.001);
      if (uRes) gl.uniform2f(uRes, canvas.width, canvas.height);
      if (uMouse) gl.uniform2f(uMouse, mouse.x, mouse.y);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      animRef.current = requestAnimationFrame(render);
    }
    animRef.current = requestAnimationFrame(render);

    return () => {
      cancelAnimationFrame(animRef.current);
      ro.disconnect();
      window.removeEventListener("mousemove", onMouse);
      const ext = gl.getExtension("WEBGL_lose_context");
      if (ext) ext.loseContext();
    };
  }, [variant]);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 w-full h-full pointer-events-none ${className}`}
      style={{ display: "block" }}
    />
  );
}
