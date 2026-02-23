<script>
  import { onMount } from "svelte";

  let ready = false;

  const bootModes = [
    {
      name: "uDOS TUI",
      role: "Primary control plane",
      detail: "Alpine-based, minimal, offline-first. Handles partitioning and install flows.",
      status: "default"
    },
    {
      name: "Windows 10",
      role: "Gaming and media",
      detail: "Console-style profile with Kodi, WantMyMTV, and game launchers.",
      status: "secondary"
    },
    {
      name: "Ubuntu Wizard",
      role: "Local orchestration",
      detail: "Runs Wizard Server for provisioning, networking, and device sync.",
      status: "secondary"
    }
  ];

  const partitions = [
    { label: "ESP", size: "512 MB", fs: "FAT32", purpose: "EFI boot + loaders" },
    { label: "UDOS_RO", size: "6-8 GB", fs: "squashfs", purpose: "uDOS TUI image" },
    { label: "UDOS_RW", size: "4-8 GB", fs: "ext4", purpose: "uDOS persistence" },
    { label: "WIZARD", size: "16-24 GB", fs: "ext4", purpose: "Ubuntu Wizard image" },
    { label: "WIN10", size: "32-64 GB", fs: "NTFS", purpose: "Windows install or WTG" },
    { label: "MEDIA", size: "8-32 GB", fs: "exFAT", purpose: "ROMs, ISOs, media" },
    { label: "CACHE", size: "remainder", fs: "ext4", purpose: "logs and downloads" }
  ];

  const devices = [
    {
      id: "dell-optiplex-9020",
      vendor: "Dell",
      boot: "UEFI",
      windows: "install",
      media: "htpc"
    },
    {
      id: "lenovo-m720q",
      vendor: "Lenovo",
      boot: "UEFI",
      windows: "wtg",
      media: "retro"
    },
    {
      id: "tp-link-wr841n",
      vendor: "TP-Link",
      boot: "Legacy",
      windows: "none",
      media: "none"
    }
  ];

  onMount(() => {
    ready = true;
  });
</script>

<main class={`min-h-screen px-6 pb-20 pt-10 transition-all duration-700 ${ready ? "opacity-100" : "opacity-0"}`}>
  <section class="mx-auto flex max-w-6xl flex-col gap-8">
    <header class="flex flex-col gap-4">
      <div class="flex items-center gap-3 text-xs uppercase tracking-[0.3em] text-neon-blue">
        <span class="h-[1px] w-10 bg-neon-blue"></span>
        Sonic Screwdriver
      </div>
      <div class="flex flex-col gap-3">
        <h1 class="text-4xl font-semibold text-white md:text-5xl">
          Standalone boot system for uDOS, Windows, and Wizard.
        </h1>
        <p class="max-w-2xl text-sm text-slate-300 md:text-base">
          Ventoy-free multi-partition builds, device-aware flashing guidance, and a retro-grade
          control surface designed for gaming and media consoles.
        </p>
      </div>
      <div class="flex flex-wrap gap-3">
        <button class="glass px-4 py-2 text-xs uppercase tracking-[0.2em] text-neon-green shadow-glow">
          Create build plan
        </button>
        <button class="glass px-4 py-2 text-xs uppercase tracking-[0.2em] text-slate-200">
          Open device catalog
        </button>
      </div>
    </header>

    <section class="grid gap-6 md:grid-cols-3">
      {#each bootModes as mode}
        <div class="glass scanline flex flex-col gap-3 rounded-xl p-5">
          <div class="flex items-center justify-between">
            <span class="text-lg font-semibold text-white">{mode.name}</span>
            <span class={`text-[10px] uppercase tracking-[0.2em] ${mode.status === "default" ? "text-neon-green" : "text-slate-400"}`}>
              {mode.status === "default" ? "default" : "ready"}
            </span>
          </div>
          <p class="text-xs uppercase tracking-[0.2em] text-slate-400">{mode.role}</p>
          <p class="text-sm text-slate-300">{mode.detail}</p>
          <button class="mt-2 w-fit rounded-full border border-neon-blue/30 px-3 py-1 text-xs uppercase tracking-[0.2em] text-neon-blue">
            Boot config
          </button>
        </div>
      {/each}
    </section>

    <section class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <div class="glass rounded-xl p-6">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-white">Partition layout v2</h2>
          <span class="text-xs uppercase tracking-[0.2em] text-slate-400">custom layout</span>
        </div>
        <div class="mt-5 space-y-3">
          {#each partitions as part}
            <div class="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-white/5 bg-ink-900/60 px-4 py-3">
              <div>
                <p class="text-sm font-semibold text-white">{part.label}</p>
                <p class="text-xs text-slate-400">{part.purpose}</p>
              </div>
              <div class="text-right text-xs text-slate-300">
                <p>{part.size}</p>
                <p class="text-neon-blue">{part.fs}</p>
              </div>
            </div>
          {/each}
        </div>
      </div>

      <div class="glass rounded-xl p-6">
        <h2 class="text-xl font-semibold text-white">Build pulse</h2>
        <ul class="mt-4 space-y-3 text-sm text-slate-300">
          <li>Plan: USB detected and validated</li>
          <li>Stage 1: Partition table (UEFI only)</li>
          <li>Stage 2: uDOS image + persistence</li>
          <li>Stage 3: Windows payload + media pack</li>
          <li>Stage 4: Wizard image and boot entries</li>
        </ul>
        <div class="mt-6 rounded-lg border border-white/5 bg-ink-900/70 p-4 text-xs text-slate-400">
          Windows media extension uses Wizard networking, VPN routing, and ad-blocking gateway profiles.
        </div>
      </div>
    </section>

    <section class="glass rounded-xl p-6">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 class="text-xl font-semibold text-white">Device database snapshot</h2>
          <p class="text-sm text-slate-400">Windows readiness and media flags are now first-class.</p>
        </div>
        <button class="rounded-full border border-white/10 px-4 py-2 text-xs uppercase tracking-[0.2em] text-slate-200">
          Sync catalog
        </button>
      </div>
      <div class="mt-4 overflow-hidden rounded-lg border border-white/5">
        <table class="w-full text-left text-xs text-slate-300">
          <thead class="bg-ink-900/80 text-[10px] uppercase tracking-[0.2em] text-slate-500">
            <tr>
              <th class="px-4 py-3">Device</th>
              <th class="px-4 py-3">Vendor</th>
              <th class="px-4 py-3">Boot</th>
              <th class="px-4 py-3">Windows</th>
              <th class="px-4 py-3">Media</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5">
            {#each devices as device}
              <tr class="bg-ink-900/40">
                <td class="px-4 py-3 font-semibold text-white">{device.id}</td>
                <td class="px-4 py-3">{device.vendor}</td>
                <td class="px-4 py-3">{device.boot}</td>
                <td class="px-4 py-3 text-neon-blue">{device.windows}</td>
                <td class="px-4 py-3 text-neon-green">{device.media}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </section>
  </section>
</main>
