/**
 * HealthInsight v2 — WebGL Liquid / Water Flow Cursor Reactive Animation
 * Powered by Three.js (r160).
 * Simulates an interactive fluid particle membrane responding to mouse momentum.
 */

(function () {
  let scene, camera, renderer;
  let particles, geometry, material;
  let positions, basePositions, velocities;
  
  const PARTICLE_COUNT = 9000;
  const GRID_X = 100;
  const GRID_Y = 90;
  const SPACING_X = 35;
  const SPACING_Y = 25;
  
  // Mouse tracking and fluid wake state
  const mouse = {
    x: 0,
    y: 0,
    targetX: 0,
    targetY: 0,
    prevX: 0,
    prevY: 0,
    speed: 0,
    radius: 280,
    force: 180
  };
  
  let clock;

  function initThree() {
    const canvas = document.getElementById('webgl-canvas');
    if (!canvas) return;

    clock = new THREE.Clock();

    // Scene setup
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x050B18, 0.0006);

    // Camera setup
    camera = new THREE.PerspectiveCamera(
      55,
      window.innerWidth / window.innerHeight,
      1,
      4000
    );
    camera.position.set(0, -200, 950);
    camera.lookAt(0, 50, 0);

    // Renderer setup
    renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      antialias: true,
      alpha: true,
      powerPreference: "high-performance"
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Create Fluid Particle Grid
    createFluidParticles();

    // Event listeners
    window.addEventListener('resize', onWindowResize, false);
    window.addEventListener('mousemove', onMouseMove, false);
    window.addEventListener('touchmove', onTouchMove, { passive: true });

    // Start animation loop
    animate();
  }

  function createFluidParticles() {
    geometry = new THREE.BufferGeometry();
    positions = new Float32Array(PARTICLE_COUNT * 3);
    basePositions = new Float32Array(PARTICLE_COUNT * 3);
    velocities = new Float32Array(PARTICLE_COUNT * 3);
    const colors = new Float32Array(PARTICLE_COUNT * 3);

    const color1 = new THREE.Color(0x00D4FF); // Cyan electric
    const color2 = new THREE.Color(0x8B5CF6); // Royal Violet
    const color3 = new THREE.Color(0x0E7490); // Deep Teal

    let index = 0;
    const startX = -(GRID_X * SPACING_X) / 2;
    const startY = -(GRID_Y * SPACING_Y) / 2;

    for (let iy = 0; iy < GRID_Y; iy++) {
      for (let ix = 0; ix < GRID_X; ix++) {
        if (index >= PARTICLE_COUNT) break;

        const x = startX + ix * SPACING_X + (Math.random() - 0.5) * 6;
        const y = startY + iy * SPACING_Y + (Math.random() - 0.5) * 6;
        const z = (Math.random() - 0.5) * 40;

        const i3 = index * 3;
        positions[i3] = x;
        positions[i3 + 1] = y;
        positions[i3 + 2] = z;

        basePositions[i3] = x;
        basePositions[i3 + 1] = y;
        basePositions[i3 + 2] = z;

        velocities[i3] = 0;
        velocities[i3 + 1] = 0;
        velocities[i3 + 2] = 0;

        // Gradient coloring from cyan to violet along diagonal
        const factor = (ix / GRID_X + iy / GRID_Y) * 0.5;
        const mixed = color1.clone().lerp(color2, factor).lerp(color3, Math.sin(factor * Math.PI) * 0.3);

        colors[i3] = mixed.r;
        colors[i3 + 1] = mixed.g;
        colors[i3 + 2] = mixed.b;

        index++;
      }
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Particle sprite generation using canvas for soft glow
    const spriteCanvas = document.createElement('canvas');
    spriteCanvas.width = 64;
    spriteCanvas.height = 64;
    const ctx = spriteCanvas.getContext('2d');
    const grad = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
    grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
    grad.addColorStop(0.2, 'rgba(0, 212, 255, 0.8)');
    grad.addColorStop(0.6, 'rgba(139, 92, 246, 0.2)');
    grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(32, 32, 32, 0, Math.PI * 2);
    ctx.fill();

    const texture = new THREE.CanvasTexture(spriteCanvas);

    material = new THREE.PointsMaterial({
      size: 14,
      vertexColors: true,
      map: texture,
      transparent: true,
      opacity: 0.65,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    particles = new THREE.Points(geometry, material);
    scene.add(particles);
  }

  function onMouseMove(e) {
    // Convert 2D screen coordinate to 3D world space approximately on particle plane
    const normX = (e.clientX / window.innerWidth) * 2 - 1;
    const normY = -(e.clientY / window.innerHeight) * 2 + 1;

    mouse.targetX = normX * 850;
    mouse.targetY = normY * 550;

    const dx = mouse.targetX - mouse.prevX;
    const dy = mouse.targetY - mouse.prevY;
    mouse.speed = Math.min(Math.sqrt(dx * dx + dy * dy), 90);

    mouse.prevX = mouse.targetX;
    mouse.prevY = mouse.targetY;
  }

  function onTouchMove(e) {
    if (e.touches.length > 0) {
      const touch = e.touches[0];
      const normX = (touch.clientX / window.innerWidth) * 2 - 1;
      const normY = -(touch.clientY / window.innerHeight) * 2 + 1;
      mouse.targetX = normX * 850;
      mouse.targetY = normY * 550;
    }
  }

  function onWindowResize() {
    if (!camera || !renderer) return;
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  }

  function animate() {
    requestAnimationFrame(animate);

    const elapsedTime = clock.getElapsedTime();
    
    // Smooth cursor interpolation
    mouse.x += (mouse.targetX - mouse.x) * 0.12;
    mouse.y += (mouse.targetY - mouse.y) * 0.12;

    const posAttr = geometry.attributes.position;
    const pos = posAttr.array;

    const radiusSq = mouse.radius * mouse.radius;
    const forceFactor = (mouse.force + mouse.speed * 1.5);

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const i3 = i * 3;

      const baseX = basePositions[i3];
      const baseY = basePositions[i3 + 1];
      const baseZ = basePositions[i3 + 2];

      // 1. Natural gentle water undulating currents
      const waveZ = Math.sin(baseX * 0.006 + elapsedTime * 1.2) * 22
                  + Math.cos(baseY * 0.007 + elapsedTime * 1.0) * 18
                  + Math.sin((baseX + baseY) * 0.004 + elapsedTime * 1.5) * 12;

      // 2. Liquid cursor displacement calculation
      const dx = pos[i3] - mouse.x;
      const dy = pos[i3 + 1] - mouse.y;
      const distSq = dx * dx + dy * dy;

      if (distSq < radiusSq) {
        const dist = Math.sqrt(distSq);
        const normDist = (1 - dist / mouse.radius);
        const ripple = Math.sin(normDist * Math.PI) * forceFactor;

        // Repel outward fluidly
        const angle = Math.atan2(dy, dx);
        velocities[i3] += Math.cos(angle) * ripple * 0.12;
        velocities[i3 + 1] += Math.sin(angle) * ripple * 0.12;
        velocities[i3 + 2] += ripple * 0.6; // Splash upward
      }

      // 3. Elastic spring physics returning to base position with fluid damping
      const returnForceX = (baseX - pos[i3]) * 0.06;
      const returnForceY = (baseY - pos[i3 + 1]) * 0.06;
      const targetZ = baseZ + waveZ;
      const returnForceZ = (targetZ - pos[i3 + 2]) * 0.08;

      velocities[i3] = (velocities[i3] + returnForceX) * 0.86; // Viscous damping
      velocities[i3 + 1] = (velocities[i3 + 1] + returnForceY) * 0.86;
      velocities[i3 + 2] = (velocities[i3 + 2] + returnForceZ) * 0.88;

      pos[i3] += velocities[i3];
      pos[i3 + 1] += velocities[i3 + 1];
      pos[i3 + 2] += velocities[i3 + 2];
    }

    posAttr.needsUpdate = true;

    // Slight cinematic camera sway
    camera.position.x = Math.sin(elapsedTime * 0.25) * 60 + (mouse.x * 0.04);
    camera.position.y = -200 + Math.cos(elapsedTime * 0.2) * 30 + (mouse.y * 0.04);
    camera.lookAt(0, 30, 0);

    renderer.render(scene, camera);
  }

  // Initialize on DOM load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThree);
  } else {
    initThree();
  }
})();
