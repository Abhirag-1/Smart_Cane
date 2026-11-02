# -*- coding: utf-8 -*-
"""
Smart Cane Firmware Function & Architecture Manual PDF Generator
Generates comprehensive, publication-quality PDF documentation covering all
functions and architectural modules in the Smart Cane firmware.
"""

import os
import subprocess
import sys

def build_html():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Smart Cane Firmware - Function & Architecture Documentation</title>
<style>
  @page {
    size: A4 portrait;
    margin: 18mm 14mm 18mm 14mm;
    @top-right {
      content: "Smart Cane Firmware Technical Manual";
      font-size: 8pt;
      color: #64748B;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    @bottom-center {
      content: "Page " counter(page);
      font-size: 8.5pt;
      color: #64748B;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
  }

  * {
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 9.5pt;
    line-height: 1.5;
    color: #1E293B;
    background-color: #FFFFFF;
    margin: 0;
    padding: 0;
  }

  .page-break {
    page-break-before: always;
  }

  .avoid-break {
    break-inside: avoid;
    page-break-inside: avoid;
  }

  /* Cover Page */
  .cover-container {
    padding-top: 40px;
    padding-bottom: 20px;
    page-break-after: always;
  }

  .cover-header {
    border-bottom: 4px solid #0284C7;
    padding-bottom: 25px;
  }

  .cover-badge {
    display: inline-block;
    background: #E0F2FE;
    color: #0369A1;
    font-size: 10pt;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
  }

  .cover-title {
    font-size: 26pt;
    font-weight: 800;
    color: #0F172A;
    margin: 0 0 10px 0;
    line-height: 1.2;
  }

  .cover-subtitle {
    font-size: 13pt;
    font-weight: 400;
    color: #475569;
    margin: 0;
  }

  .cover-meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 20px;
    margin: 35px 0 25px 0;
  }

  .meta-item {
    font-size: 9pt;
  }
  .meta-label {
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    font-size: 7.5pt;
    letter-spacing: 0.5px;
  }
  .meta-value {
    font-size: 10pt;
    font-weight: 600;
    color: #0F172A;
    margin-top: 2px;
  }

  .cover-summary {
    color: #334155;
    font-size: 9.5pt;
    line-height: 1.6;
    margin: 25px 0;
    background: #F1F5F9;
    padding: 16px;
    border-radius: 6px;
    border-left: 4px solid #0284C7;
  }

  .cover-footer {
    margin-top: 40px;
    border-top: 1px solid #E2E8F0;
    padding-top: 15px;
    display: flex;
    justify-content: space-between;
    font-size: 8.5pt;
    color: #64748B;
  }

  /* Section Headers */
  h1 {
    font-size: 16pt;
    font-weight: 800;
    color: #0F172A;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 6px;
    margin-top: 24px;
    margin-bottom: 12px;
  }

  h2 {
    font-size: 12.5pt;
    font-weight: 700;
    color: #0369A1;
    margin-top: 18px;
    margin-bottom: 8px;
  }

  h3 {
    font-size: 10.5pt;
    font-weight: 700;
    color: #334155;
    margin-top: 14px;
    margin-bottom: 6px;
  }

  p {
    margin: 0 0 10px 0;
    color: #334155;
  }

  /* Function Card */
  .func-card {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-left: 4px solid #0284C7;
    border-radius: 6px;
    padding: 12px 14px;
    margin-bottom: 14px;
    break-inside: avoid;
    page-break-inside: avoid;
  }

  .func-card.isr {
    border-left-color: #EF4444;
  }
  .func-card.hal {
    border-left-color: #10B981;
  }
  .func-card.system {
    border-left-color: #8B5CF6;
  }
  .func-card.posix {
    border-left-color: #64748B;
  }

  .func-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 6px;
    flex-wrap: wrap;
    gap: 6px;
  }

  .func-name {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-size: 11pt;
    font-weight: 700;
    color: #0F172A;
  }

  .badges {
    display: flex;
    gap: 5px;
  }

  .badge {
    font-size: 7pt;
    font-weight: 700;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 3px;
    letter-spacing: 0.5px;
  }

  .badge-app { background: #E0F2FE; color: #0284C7; }
  .badge-hal { background: #D1FAE5; color: #059669; }
  .badge-isr { background: #FEE2E2; color: #DC2626; }
  .badge-sys { background: #EDE9FE; color: #7C3AED; }
  .badge-posix { background: #F1F5F9; color: #475569; }
  .badge-file { background: #F1F5F9; color: #475569; border: 1px solid #E2E8F0; }

  .func-sig {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 4px;
    padding: 6px 10px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 8.5pt;
    color: #0F172A;
    margin-bottom: 8px;
    word-break: break-all;
  }

  .func-desc {
    font-size: 9pt;
    color: #334155;
    margin-bottom: 8px;
    line-height: 1.45;
  }

  .func-grid {
    display: grid;
    grid-template-columns: 110px 1fr;
    gap: 4px 10px;
    font-size: 8.5pt;
    background: #FAFAFA;
    padding: 8px 10px;
    border-radius: 4px;
    border: 1px solid #F1F5F9;
  }

  .func-grid-label {
    font-weight: 600;
    color: #64748B;
  }

  .func-grid-value {
    color: #1E293B;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 8.5pt;
    margin: 10px 0 16px 0;
  }

  th, td {
    padding: 6px 8px;
    text-align: left;
    border-bottom: 1px solid #E2E8F0;
  }

  th {
    background-color: #F8FAFC;
    color: #475569;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 7.5pt;
    letter-spacing: 0.5px;
    border-top: 1px solid #CBD5E1;
    border-bottom: 2px solid #CBD5E1;
  }

  tr:nth-child(even) td {
    background-color: #FBFCFD;
  }

  code {
    font-family: "SFMono-Regular", Consolas, monospace;
    font-size: 8.5pt;
    background: #F1F5F9;
    padding: 1px 4px;
    border-radius: 3px;
    color: #0369A1;
  }

  .diagram-container {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 12px;
    margin: 12px 0;
    text-align: center;
  }
</style>
</head>
<body>

<!-- ========================================== -->
<!-- COVER PAGE                                 -->
<!-- ========================================== -->
<div class="cover-container">
  <div class="cover-header">
    <div class="cover-badge">STM32 Embedded Firmware Manual</div>
    <h1 class="cover-title">Smart Cane Assistive System</h1>
    <p class="cover-subtitle">Complete Program Architecture, Subsystems &amp; Function Reference</p>
  </div>

  <div class="cover-meta-grid">
    <div class="meta-item">
      <div class="meta-label">Target Microcontroller</div>
      <div class="meta-value">STM32F103C8T6 (ARM Cortex-M3 @ 8 MHz HSI)</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Primary Peripherals</div>
      <div class="meta-value">HC-SR04, NEO-6M GPS, HC-05 BT, TIM2, SysTick</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Total Functions Cataloged</div>
      <div class="meta-value">46 Distinct Functions Across 9 C Modules</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Firmware Architecture</div>
      <div class="meta-value">Bare-Metal Superloop + 1ms SysTick Timebase</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Toolchain &amp; IDE</div>
      <div class="meta-value">STM32CubeIDE / GNU ARM Embedded Toolchain</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Document Date &amp; Status</div>
      <div class="meta-value">November 2026 &bull; Production Release</div>
    </div>
  </div>

  <div class="cover-summary">
    <strong>Executive Summary:</strong> The Smart Cane firmware is a high-reliability, real-time embedded solution designed to aid visually impaired individuals with spatial awareness, collision avoidance, and personal safety. The system performs ultrasonic obstacle detection, satellite telemetry capture with an anti-glitch jump filter, Bluetooth serial telemetry streaming, and a dual-mode emergency SOS state machine with a 5-second false-alarm cancel window. This document details every function, algorithm, hardware register interaction, and calling relationship within the software.
  </div>

  <div class="cover-footer">
    <span>Smart Cane Engineering &bull; Firmware Subsystem</span>
    <span>STM32F103C8T6 Architecture</span>
  </div>
</div>

<!-- ========================================== -->
<!-- 1. SYSTEM ARCHITECTURE & PERIPHERALS       -->
<!-- ========================================== -->
<h1>1. System Architecture &amp; Hardware Pinout</h1>
<p>
  The system firmware runs directly on the ARM Cortex-M3 silicon without RTOS scheduling jitter, using direct hardware register access for microsecond pulse measurement and non-blocking state machines for serial processing.
</p>

<h2>1.1 Microcontroller Pin Configuration</h2>
<table>
  <thead>
    <tr>
      <th>Signal / Pin</th>
      <th>Peripheral</th>
      <th>Hardware Mode</th>
      <th>Operational Role</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>PA0</code></td>
      <td>HC-SR04 Trig</td>
      <td>GPIO Output Push-Pull (2 MHz)</td>
      <td>Issues 20 &mu;s trigger pulse every 100 ms to start distance measurement</td>
    </tr>
    <tr>
      <td><code>PA1</code></td>
      <td>HC-SR04 Echo</td>
      <td>GPIO Input Floating</td>
      <td>Receives ultrasonic echo pulse width; timed by TIM2 with 1 &mu;s resolution</td>
    </tr>
    <tr>
      <td><code>PA2</code></td>
      <td>HC-05 BT TX</td>
      <td>USART2 TX (AF Push-Pull, 50 MHz)</td>
      <td>Transmits telemetry, warnings, and GPS data at 9600 baud (8-N-1)</td>
    </tr>
    <tr>
      <td><code>PA3</code></td>
      <td>HC-05 BT RX</td>
      <td>USART2 RX (Input Pull-Up)</td>
      <td>Receives configuration or handshakes from paired smartphone/receiver</td>
    </tr>
    <tr>
      <td><code>PA9</code></td>
      <td>NEO-6M GPS TX</td>
      <td>USART1 TX (AF Push-Pull, 50 MHz)</td>
      <td>Sends NMEA configuration commands to GPS receiver (9600 baud)</td>
    </tr>
    <tr>
      <td><code>PA10</code></td>
      <td>NEO-6M GPS RX</td>
      <td>USART1 RX (Input Pull-Up)</td>
      <td>Receives streaming NMEA-0183 sentences ($GPRMC/$GNRMC) at 9600 baud</td>
    </tr>
    <tr>
      <td><code>PB1</code></td>
      <td>SOS Button</td>
      <td>GPIO Input with Internal Pull-Up</td>
      <td>Emergency input line; supports momentary push buttons or toggle switches</td>
    </tr>
    <tr>
      <td><code>PC13</code></td>
      <td>Status LED</td>
      <td>GPIO Output Push-Pull (2 MHz)</td>
      <td>Active-LOW indicator: solid ON during obstacle proximity; 128 ms strobe during SOS</td>
    </tr>
  </tbody>
</table>

<h2>1.2 System Control &amp; Dataflow Diagram</h2>
<div class="diagram-container">
  <svg width="600" height="170" viewBox="0 0 600 170" style="max-width: 100%; height: auto;">
    <rect x="15" y="15" width="115" height="45" rx="5" fill="#E0F2FE" stroke="#0284C7" stroke-width="1.5"/>
    <text x="72" y="36" font-family="sans-serif" font-size="10" font-weight="700" fill="#0369A1" text-anchor="middle">HC-SR04</text>
    <text x="72" y="50" font-family="sans-serif" font-size="8" fill="#0284C7" text-anchor="middle">PA0 Trig / PA1 Echo</text>

    <rect x="15" y="105" width="115" height="45" rx="5" fill="#E0F2FE" stroke="#0284C7" stroke-width="1.5"/>
    <text x="72" y="126" font-family="sans-serif" font-size="10" font-weight="700" fill="#0369A1" text-anchor="middle">NEO-6M GPS</text>
    <text x="72" y="140" font-family="sans-serif" font-size="8" fill="#0284C7" text-anchor="middle">USART1 (PA9/PA10)</text>

    <rect x="220" y="20" width="160" height="130" rx="8" fill="#F8FAFC" stroke="#0F172A" stroke-width="2"/>
    <text x="300" y="44" font-family="sans-serif" font-size="11" font-weight="800" fill="#0F172A" text-anchor="middle">STM32F103C8T6</text>
    <text x="300" y="58" font-family="sans-serif" font-size="8" fill="#475569" text-anchor="middle">ARM Cortex-M3 Superloop</text>
    <line x1="230" y1="67" x2="370" y2="67" stroke="#CBD5E1" stroke-width="1"/>
    <text x="300" y="84" font-family="sans-serif" font-size="8.5" font-weight="600" fill="#0369A1" text-anchor="middle">&bull; SysTick 1ms Timebase</text>
    <text x="300" y="99" font-family="sans-serif" font-size="8.5" font-weight="600" fill="#059669" text-anchor="middle">&bull; TIM2 1&mu;s Ultrasonic Timer</text>
    <text x="300" y="114" font-family="sans-serif" font-size="8.5" font-weight="600" fill="#D97706" text-anchor="middle">&bull; Jump Filter (1.85km)</text>
    <text x="300" y="129" font-family="sans-serif" font-size="8.5" font-weight="600" fill="#DC2626" text-anchor="middle">&bull; SOS State Machine</text>

    <rect x="465" y="15" width="120" height="45" rx="5" fill="#D1FAE5" stroke="#059669" stroke-width="1.5"/>
    <text x="525" y="36" font-family="sans-serif" font-size="10" font-weight="700" fill="#065F46" text-anchor="middle">HC-05 Bluetooth</text>
    <text x="525" y="50" font-family="sans-serif" font-size="8" fill="#059669" text-anchor="middle">USART2 (PA2/PA3)</text>

    <rect x="465" y="105" width="120" height="45" rx="5" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5"/>
    <text x="525" y="126" font-family="sans-serif" font-size="10" font-weight="700" fill="#991B1B" text-anchor="middle">Alert &amp; SOS</text>
    <text x="525" y="140" font-family="sans-serif" font-size="8" fill="#DC2626" text-anchor="middle">PC13 LED &amp; PB1 Button</text>

    <path d="M 130 37 L 220 37" stroke="#0284C7" stroke-width="1.5"/>
    <path d="M 130 127 L 220 127" stroke="#0284C7" stroke-width="1.5"/>
    <path d="M 380 37 L 465 37" stroke="#059669" stroke-width="1.5"/>
    <path d="M 380 127 L 465 127" stroke="#DC2626" stroke-width="1.5"/>
  </svg>
</div>

<!-- ========================================== -->
<!-- 2. CORE APPLICATION FUNCTIONS              -->
<!-- ========================================== -->
<div class="page-break"></div>

<h1>2. Core Application Functions (Src/main.c &amp; Inc/main.h)</h1>
<p>
  The core application functions manage real-time hardware execution, timing coordination, sensor algorithms, and wireless communications.
</p>

<!-- main() -->
<div class="func-card">
  <div class="func-header">
    <span class="func-name">main</span>
    <div class="badges">
      <span class="badge badge-app">Main Entry</span>
      <span class="badge badge-file">main.c:614</span>
    </div>
  </div>
  <div class="func-sig">int main(void)</div>
  <div class="func-desc">
    Primary program entry point. Initializes MCU hardware registers via <code>System_Init()</code> and enters the infinite non-blocking superloop to execute all sub-tasks in round-robin fashion.
  </div>
  <div class="func-grid">
    <div class="func-grid-label">Calling Pattern:</div>
    <div class="func-grid-value">Invoked by CMSIS startup code <code>Reset_Handler</code> after stack and data/BSS initialization.</div>
    <div class="func-grid-label">Task Sequence:</div>
    <div class="func-grid-value">
      1. <code>Process_Emergency_Button()</code>: Checks for PB1 button press or release.<br>
      2. <strong>GPS Serial Polling:</strong> Tests <code>USART1-&gt;SR &amp; (1 &lt;&lt; 5)</code> (RXNE flag). If a byte arrived, extracts it from <code>USART1-&gt;DR</code> and calls <code>Process_GPS_Byte()</code>.<br>
      3. <code>Process_SysTick()</code>: Checks 1ms tick flag, updates countdowns and flash rates.<br>
      4. <code>Process_Ultrasonic()</code>: Triggers HC-SR04 pulse and reads echo return.
    </div>
    <div class="func-grid-label">Concurrency:</div>
    <div class="func-grid-value">100% non-blocking cooperative execution.</div>
  </div>
</div>

<!-- System_Init() -->
<div class="func-card">
  <div class="func-header">
    <span class="func-name">System_Init</span>
    <div class="badges">
      <span class="badge badge-app">Init Engine</span>
      <span class="badge badge-file">main.c:61</span>
    </div>
  </div>
  <div class="func-sig">void System_Init(void)</div>
  <div class="func-desc">
    Performs bare-metal register-level initialization of clocks, GPIO pins, SysTick, TIM2, and dual USART peripherals for maximum boot speed and zero HAL runtime overhead.
  </div>
  <div class="func-grid">
    <div class="func-grid-label">Hardware Setup:</div>
    <div class="func-grid-value">
      &bull; <strong>RCC Clocks:</strong> Powers APB2 (AFIO, GPIOA, GPIOB, GPIOC, USART1) and APB1 (TIM2, USART2).<br>
      &bull; <strong>GPIOA Configuration:</strong> PA0=Output PP 2MHz, PA1=Input Floating, PA2=AF-PP (USART2 TX), PA3=Input Pull-Up (USART2 RX), PA9=AF-PP (USART1 TX), PA10=Input Pull-Up (USART1 RX).<br>
      &bull; <strong>GPIOB Configuration:</strong> PB1 set to Input Pull-up mode (ODR=1).<br>
      &bull; <strong>GPIOC Configuration:</strong> PC13 set to Output PP 2MHz, set HIGH (active-low LED initially OFF).<br>
      &bull; <strong>SysTick:</strong> LOAD=7999 (1ms @ 8MHz), VAL=0, CTRL=5 (CPU clock, enabled).<br>
      &bull; <strong>TIM2:</strong> PSC=7 (1&mu;s tick @ 8MHz), ARR=0xFFFF, EGR=1 (prescaler reload).<br>
      &bull; <strong>USART1 &amp; 2:</strong> Baud rate divisor BRR=0x0341 (9600 baud @ 8MHz), CR1=0x200C (UE, TE, RE).<br>
      &bull; <strong>Banner:</strong> Transmits welcome banner over Bluetooth upon completion.
    </div>
    <div class="func-grid-label">Registers Modified:</div>
    <div class="func-grid-value"><code>RCC-&gt;APB1ENR</code>, <code>RCC-&gt;APB2ENR</code>, <code>GPIOA/B/C-&gt;CRL/CRH/BSRR</code>, <code>SysTick-&gt;*</code>, <code>TIM2-&gt;*</code>, <code>USART1/2-&gt;*</code></div>
  </div>
</div>

<!-- Process_Ultrasonic() -->
<div class="func-card">
  <div class="func-header">
    <span class="func-name">Process_Ultrasonic</span>
    <div class="badges">
      <span class="badge badge-app">Proximity Sensor</span>
      <span class="badge badge-file">main.c:530</span>
    </div>
  </div>
  <div class="func-sig">void Process_Ultrasonic(void)</div>
  <div class="func-desc">
    Non-blocking 100ms trigger and echo measurement engine for the HC-SR04 sensor. Accurately determines distance in centimeters using TIM2 microsecond counting and triggers proximity warnings.
  </div>
  <div class="func-grid">
    <div class="func-grid-label">Algorithm:</div>
    <div class="func-grid-value">
      1. <strong>Safety Interlock:</strong> Halts immediately if <code>emergency_state != EMERGENCY_STATE_NORMAL</code>.<br>
      2. <strong>Periodic Gate:</strong> Executes only when <code>ultrasonic_timer &ge; 100 ms</code>.<br>
      3. <strong>Trigger Generation:</strong> Pulses PA0 HIGH for 20 &mu;s using calibrated NOP loop, then brings PA0 LOW.<br>
      4. <strong>Echo Start Wait:</strong> Polls PA1 until HIGH (timeout: 35,000 iterations &approx; 25 ms).<br>
      5. <strong>TIM2 Microsecond Timing:</strong> Resets counter to 0, enables CEN=1, and waits for PA1 to fall LOW (timeout: 45,000 &mu;s). Stops TIM2 and stores count.<br>
      6. <strong>Glitch Suppression:</strong> Discards echo pulses &lt;116 &mu;s (&lt;2 cm blind zone).<br>
      7. <strong>Distance Math:</strong> Calculates distance in cm: <code>(raw_echo_us + 29) / 58</code> (rounded to nearest integer).<br>
      8. <strong>Alert Logic:</strong> If distance is between 2 cm and 50 cm: illuminates PC13 LED; if <code>alert_cooldown &ge; 500 ms</code>, emits <code>[ALERT] Obstacle: XX cm\r\n</code> over Bluetooth.
    </div>
    <div class="func-grid-label">Key Parameters:</div>
    <div class="func-grid-value">Min: 2 cm, Max: 50 cm, Cooldown: 500 ms, Interval: 100 ms.</div>
  </div>
</div>

<!-- Process_Emergency_Button() -->
<div class="func-card">
  <div class="func-header">
    <span class="func-name">Process_Emergency_Button</span>
    <div class="badges">
      <span class="badge badge-app">Safety State Machine</span>
      <span class="badge badge-file">main.c:353</span>
    </div>
  </div>
  <div class="func-sig">void Process_Emergency_Button(void)</div>
  <div class="func-desc">
    Universal debounce and state machine engine that handles both momentary tactile buttons and physical latching toggle switches on PB1. Implements a 5-second cancel window for false alarms.
  </div>
  <div class="func-grid">
    <div class="func-grid-label">State Transitions:</div>
    <div class="func-grid-value">
      &bull; <strong>Debounce:</strong> Rejects contact bounce with a 50 ms lockout timer.<br>
      &bull; <strong>Normal &rarr; Pending SOS:</strong> First press detected: transmits <code>STR_SOS_BANNER</code>, sets state to <code>PENDING</code>, arms 5-second countdown, and triggers immediate GPS burst.<br>
      &bull; <strong>Pending &rarr; Normal (False Alarm):</strong> If button is pressed again within 5 seconds, cancels emergency, sends <code>STR_FALSE_ALARM</code>, and resets state.<br>
      &bull; <strong>Confirmed &rarr; Normal (Cleared):</strong> If button is pressed after emergency is active, resets state to Normal, transmits <code>STR_SOS_CLEARED</code>, and resumes ultrasonic sensing.<br>
      &bull; <strong>Latching Switch Discrimination:</strong> Ignores finger release duration &lt;350 ms. If a switch remained active &gt;350 ms and unlatches, treats transition as an intentional second action.
    </div>
  </div>
</div>

<!-- Process_GPS_Byte() -->
<div class="func-card">
  <div class="func-header">
    <span class="func-name">Process_GPS_Byte</span>
    <div class="badges">
      <span class="badge badge-app">GPS Stream</span>
      <span class="badge badge-file">main.c:432</span>
    </div>
  </div>
  <div class="func-sig">void Process_GPS_Byte(uint8_t byte)</div>
  <div class="func-desc">
    Serial byte-stream consumer for incoming USART1 data from the NEO-6M module. Detects NMEA sentences, manages buffer boundaries, and triggers sentence parsing.
  </div>
  <div class="func-grid">
    <div class="func-grid-label">Stream States:</div>
    <div class="func-grid-value">
      &bull; <code>GPS_STATE_IDLE</code>: Ignores incoming bytes to conserve MCU cycles between 5-second trigger intervals.<br>
      &bull; <code>GPS_STATE_WAIT_DOLLAR</code>: Waits for '$' framing start-of-sentence marker.<br>
      &bull; <code>GPS_STATE_BUFFERING</code>: Collects characters into <code>line_buf[128]</code>. Protects against buffer overrun. Upon '\n' arrival, calls <code>Parse_RMC()</code>.
    </div>
  </div>
</div>

<!-- Parse_RMC() -->
<div class="func-card">
  <div class="func-header">
    <span class="func-name">Parse_RMC</span>
    <div class="badges">
      <span class="badge badge-app">NMEA Tokenizer</span>
      <span class="badge badge-file">main.c:178</span>
    </div>
  </div>
  <div class="func-sig">bool Parse_RMC(char *line)</div>
  <div class="func-desc">
    High-performance zero-copy NMEA parser. Validates sentence headers and extracts GPS satellite fix status, latitude, north/south indicator, longitude, and east/west indicator.
  </div>
  <div class="func-grid">
    <div class="func-grid-label">Validation Logic:</div>
    <div class="func-grid-value">
      Validates <code>line[0] == '$'</code> and <code>line[3..5] == 'RMC'</code> (matching both <code>$GPRMC</code> and <code>$GNRMC</code>). Scans comma delimiters: Field 2 = Fix Status ('A' = Valid, 'V' = Warning), Field 3 = Latitude, Field 4 = N/S, Field 5 = Longitude, Field 6 = E/W. Terminates string fields in-place with null characters.
    </div>
    <div class="func-grid-label">Returns:</div>
    <div class="func-grid-value"><code>true</code> if sentence contains valid RMC fields with &ge;6 commas; <code>false</code> otherwise.</div>
  </div>
</div>

<!-- Filter_And_Send_GPS() -->
<div class="func-card">
  <div class="func-header">
    <span class="func-name">Filter_And_Send_GPS</span>
    <div class="badges">
      <span class="badge badge-app">Anti-Glitch Filter</span>
      <span class="badge badge-file">main.c:288</span>
    </div>
  </div>
  <div class="func-sig">void Filter_And_Send_GPS(void)</div>
  <div class="func-desc">
    Kinematic sanity filter that prevents transmission of corrupted coordinates resulting from satellite multipath, poor signal, or UART transmission noise.
  </div>
  <div class="func-grid">
    <div class="func-grid-label">Filtering Criteria:</div>
    <div class="func-grid-value">
      1. Converts latitude and longitude into total tenths of an arcminute.<br>
      2. Compares against previous baseline reading: if coordinate jump exceeds 10 tenths (&approx; 1.85 km in 5 seconds) or hemisphere character flips ('N'&rarr;'S' or 'E'&rarr;'W'), flags reading as a glitch.<br>
      3. Overrides erroneous fix with previous known-good coordinates and transmits clean data.<br>
      4. If reading is valid, updates baseline coordinates.
    </div>
  </div>
</div>

<!-- Send_Parsed_GPS() -->
<div class="func-card">
  <div class="func-header">
    <span class="func-name">Send_Parsed_GPS</span>
    <div class="badges">
      <span class="badge badge-app">Telemetry Format</span>
      <span class="badge badge-file">main.c:235</span>
    </div>
  </div>
  <div class="func-sig">void Send_Parsed_GPS(void)</div>
  <div class="func-desc">
    Formats and transmits human-readable GPS coordinates over USART2 (Bluetooth). Prepends emergency alert headers if emergency SOS is active, or outputs a searching notification if satellite lock is pending.
  </div>
  <div class="func-grid">
    <div class="func-grid-label">Output Format:</div>
    <div class="func-grid-value">
      &bull; Lock Available: <code>Lat: 1258.1234 N, Lon: 07735.5678 E\r\n</code><br>
      &bull; No Lock: <code>GPS: Searching for Satellites... (No Lock)\r\n</code><br>
      &bull; SOS Active: Prepends <code>*** [EMERGENCY GPS LOCATION] ***\r\n</code>
    </div>
  </div>
</div>

<!-- Compute_Lat_Tenths() & Compute_Lon_Tenths() -->
<div class="func-card">
  <div class="func-header">
    <span class="func-name">Compute_Lat_Tenths &amp; Compute_Lon_Tenths</span>
    <div class="badges">
      <span class="badge badge-app">Coordinate Math</span>
      <span class="badge badge-file">main.c:263, 275</span>
    </div>
  </div>
  <div class="func-sig">
    static uint32_t Compute_Lat_Tenths(const char *str)<br>
    static uint32_t Compute_Lon_Tenths(const char *str)
  </div>
  <div class="func-desc">
    High-speed integer parsing routines. Converts NMEA coordinate strings (<code>DDMM.M...</code> for latitude, <code>DDDMM.M...</code> for longitude) directly into tenths of a minute: <code>(Degrees &times; 60 + Minutes) &times; 10 + Tenths</code>.
  </div>
  <div class="func-grid">
    <div class="func-grid-label">Advantage:</div>
    <div class="func-grid-value">Eliminates floating-point library overhead; executes in &lt;1 &mu;s.</div>
  </div>
</div>

<!-- Process_SysTick() -->
<div class="func-card">
  <div class="func-header">
    <span class="func-name">Process_SysTick</span>
    <div class="badges">
      <span class="badge badge-app">Timebase</span>
      <span class="badge badge-file">main.c:478</span>
    </div>
  </div>
  <div class="func-sig">void Process_SysTick(void)</div>
  <div class="func-desc">
    Hardware SysTick polling engine. Monitors bit 16 (COUNTFLAG). Every 1 ms, advances system counters, drives the emergency countdown, operates the SOS LED strobe, and triggers periodic GPS capture.
  </div>
  <div class="func-grid">
    <div class="func-grid-label">Key Actions:</div>
    <div class="func-grid-value">
      &bull; Increments <code>ms_counter</code>, <code>gps_timer</code>, <code>ultrasonic_timer</code>, <code>alert_cooldown</code>.<br>
      &bull; Decrements <code>btn_debounce_timer</code>.<br>
      &bull; <strong>5-Second SOS Confirmation:</strong> If <code>emergency_state == PENDING</code> and timer reaches 5000 ms, promotes state to <code>CONFIRMED</code> and transmits <code>STR_SOS_CONFIRMED</code>.<br>
      &bull; <strong>LED Strobe:</strong> When emergency is active, toggles PC13 at ~128 ms intervals (tested via bit 7 of <code>ms_counter</code>).<br>
      &bull; <strong>5-Second GPS Trigger:</strong> When <code>gps_timer &ge; 5000 ms</code>, resets timer and arms GPS receiver to capture next sentence.
    </div>
  </div>
</div>

<!-- UART2 Helper Functions -->
<div class="func-card">
  <div class="func-header">
    <span class="func-name">UART2_SendChar, UART2_SendString, UART2_SendNum, UART2_Send2DigitNum</span>
    <div class="badges">
      <span class="badge badge-app">UART Drivers</span>
      <span class="badge badge-file">main.c:131, 141, 150, 164</span>
    </div>
  </div>
  <div class="func-sig">
    void UART2_SendChar(char c)<br>
    void UART2_SendString(const char *str)<br>
    void UART2_SendNum(uint32_t num)<br>
    void UART2_Send2DigitNum(uint32_t num)
  </div>
  <div class="func-desc">
    Low-latency serial transmission library. Polls TXE (bit 7 of <code>USART2-&gt;SR</code>) and writes to <code>USART2-&gt;DR</code>. Formats decimal numbers (0-999) without calling heavy <code>sprintf</code> or dynamic memory allocators.
  </div>
</div>

<!-- Error_Handler() -->
<div class="func-card">
  <div class="func-header">
    <span class="func-name">Error_Handler</span>
    <div class="badges">
      <span class="badge badge-app">Safety Trap</span>
      <span class="badge badge-file">main.c:606</span>
    </div>
  </div>
  <div class="func-sig">void Error_Handler(void)</div>
  <div class="func-desc">
    Global exception trap. Disables global interrupts via <code>__disable_irq()</code> and traps CPU in an infinite loop if peripheral hardware initialization fails.
  </div>
</div>

<!-- ========================================== -->
<!-- 3. HAL & PERIPHERAL MODULES                -->
<!-- ========================================== -->
<div class="page-break"></div>

<h1>3. Hardware Abstraction Layer Modules (Drivers)</h1>
<p>
  STM32Cube HAL driver functions that provide peripheral clock gating, alternate function multiplexing, and low-level peripheral configuration.
</p>

<!-- GPIO -->
<h2>3.1 GPIO Initialization Module (Src/gpio.c)</h2>
<div class="func-card hal">
  <div class="func-header">
    <span class="func-name">MX_GPIO_Init</span>
    <div class="badges"><span class="badge badge-hal">HAL Init</span><span class="badge badge-file">gpio.c:42</span></div>
  </div>
  <div class="func-sig">void MX_GPIO_Init(void)</div>
  <div class="func-desc">Enables peripheral clock gates for GPIOC, GPIOD, GPIOA, and GPIOB via RCC bus registers.</div>
</div>

<!-- I2C -->
<h2>3.2 I2C Peripheral Driver (Src/i2c.c)</h2>
<div class="func-card hal">
  <div class="func-header">
    <span class="func-name">MX_I2C1_Init</span>
    <div class="badges"><span class="badge badge-hal">HAL Driver</span><span class="badge badge-file">i2c.c:30</span></div>
  </div>
  <div class="func-sig">void MX_I2C1_Init(void)</div>
  <div class="func-desc">Configures I2C1 instance for 100 kHz standard mode, 7-bit addressing, duty cycle 2, general call disabled, and no-stretch mode disabled. Traps to <code>Error_Handler()</code> on error.</div>
</div>

<div class="func-card hal">
  <div class="func-header">
    <span class="func-name">HAL_I2C_MspInit &amp; HAL_I2C_MspDeInit</span>
    <div class="badges"><span class="badge badge-hal">MSP Callback</span><span class="badge badge-file">i2c.c:59, 87</span></div>
  </div>
  <div class="func-sig">
    void HAL_I2C_MspInit(I2C_HandleTypeDef* i2cHandle)<br>
    void HAL_I2C_MspDeInit(I2C_HandleTypeDef* i2cHandle)
  </div>
  <div class="func-desc">Low-level MSP hardware callbacks for I2C1. Configures PB6 (SCL) and PB7 (SDA) as alternate function open-drain, enables/disables I2C1 peripheral clock in RCC.</div>
</div>

<!-- TIM2 -->
<h2>3.3 Timer 2 Peripheral Driver (Src/tim.c)</h2>
<div class="func-card hal">
  <div class="func-header">
    <span class="func-name">MX_TIM2_Init</span>
    <div class="badges"><span class="badge badge-hal">HAL Driver</span><span class="badge badge-file">tim.c:30</span></div>
  </div>
  <div class="func-sig">void MX_TIM2_Init(void)</div>
  <div class="func-desc">Configures TIM2 general purpose timer instance, timebase clock division, and master mode trigger output (TRGO). Traps to <code>Error_Handler()</code> on error.</div>
</div>

<div class="func-card hal">
  <div class="func-header">
    <span class="func-name">HAL_TIM_Base_MspInit &amp; HAL_TIM_Base_MspDeInit</span>
    <div class="badges"><span class="badge badge-hal">MSP Callback</span><span class="badge badge-file">tim.c:70, 86</span></div>
  </div>
  <div class="func-sig">
    void HAL_TIM_Base_MspInit(TIM_HandleTypeDef* tim_baseHandle)<br>
    void HAL_TIM_Base_MspDeInit(TIM_HandleTypeDef* tim_baseHandle)
  </div>
  <div class="func-desc">Enables or disables TIM2 peripheral clock gate in <code>RCC-&gt;APB1ENR</code>.</div>
</div>

<!-- USART -->
<h2>3.4 Serial USART Drivers (Src/usart.c)</h2>
<div class="func-card hal">
  <div class="func-header">
    <span class="func-name">MX_USART1_UART_Init &amp; MX_USART2_UART_Init</span>
    <div class="badges"><span class="badge badge-hal">HAL Driver</span><span class="badge badge-file">usart.c:32, 61</span></div>
  </div>
  <div class="func-sig">
    void MX_USART1_UART_Init(void)<br>
    void MX_USART2_UART_Init(void)
  </div>
  <div class="func-desc">Initializes USART1 (GPS) and USART2 (Bluetooth) instances for 9600 baud, 8-N-1, TX/RX mode, and 16x oversampling. Traps to <code>Error_Handler()</code> on error.</div>
</div>

<div class="func-card hal">
  <div class="func-header">
    <span class="func-name">HAL_UART_MspInit &amp; HAL_UART_MspDeInit</span>
    <div class="badges"><span class="badge badge-hal">MSP Callback</span><span class="badge badge-file">usart.c:89, 155</span></div>
  </div>
  <div class="func-sig">
    void HAL_UART_MspInit(UART_HandleTypeDef* uartHandle)<br>
    void HAL_UART_MspDeInit(UART_HandleTypeDef* uartHandle)
  </div>
  <div class="func-desc">Configures GPIO pins (PA9/PA10 for USART1, PA2/PA3 for USART2), enables peripheral clock gates, and registers NVIC interrupt vectors with priority 0.</div>
</div>

<!-- HAL MSP -->
<h2>3.5 Global MCU Support Package (Src/stm32f1xx_hal_msp.c)</h2>
<div class="func-card hal">
  <div class="func-header">
    <span class="func-name">HAL_MspInit</span>
    <div class="badges"><span class="badge badge-hal">MSP Core</span><span class="badge badge-file">stm32f1xx_hal_msp.c:62</span></div>
  </div>
  <div class="func-sig">void HAL_MspInit(void)</div>
  <div class="func-desc">Global MCU Support Package initialization. Enables AFIO clock in RCC and configures NVIC priority grouping to <code>NVIC_PRIORITYGROUP_4</code> (4 bits preemption, 0 bits subpriority).</div>
</div>

<!-- ========================================== -->
<!-- 4. INTERRUPTS AND FAULTS                   -->
<!-- ========================================== -->
<div class="page-break"></div>

<h1>4. Interrupt Service Routines &amp; Cortex-M3 Faults (Src/stm32f1xx_it.c)</h1>
<p>
  Low-level vector interrupt handlers and processor fault handlers for Cortex-M3 core operations and peripheral events.
</p>

<h2>4.1 Processor Fault &amp; Exception Traps</h2>
<div class="func-card isr">
  <div class="func-header">
    <span class="func-name">NMI_Handler</span>
    <div class="badges"><span class="badge badge-isr">ISR</span><span class="badge badge-file">stm32f1xx_it.c:70</span></div>
  </div>
  <div class="func-sig">void NMI_Handler(void)</div>
  <div class="func-desc">Non-Maskable Interrupt handler. Traps execution in an infinite loop upon critical hardware signals.</div>
</div>

<div class="func-card isr">
  <div class="func-header">
    <span class="func-name">HardFault_Handler</span>
    <div class="badges"><span class="badge badge-isr">Fatal Fault</span><span class="badge badge-file">stm32f1xx_it.c:85</span></div>
  </div>
  <div class="func-sig">void HardFault_Handler(void)</div>
  <div class="func-desc">Fatal hardware fault trap. Catches unrecoverable errors (invalid vector fetch, escalated faults, bus errors) in an infinite loop.</div>
</div>

<div class="func-card isr">
  <div class="func-header">
    <span class="func-name">MemManage_Handler</span>
    <div class="badges"><span class="badge badge-isr">MPU Fault</span><span class="badge badge-file">stm32f1xx_it.c:100</span></div>
  </div>
  <div class="func-sig">void MemManage_Handler(void)</div>
  <div class="func-desc">Memory Protection Unit (MPU) fault trap. Halts CPU upon memory access rule violations.</div>
</div>

<div class="func-card isr">
  <div class="func-header">
    <span class="func-name">BusFault_Handler</span>
    <div class="badges"><span class="badge badge-isr">Bus Fault</span><span class="badge badge-file">stm32f1xx_it.c:115</span></div>
  </div>
  <div class="func-sig">void BusFault_Handler(void)</div>
  <div class="func-desc">Memory bus fault handler. Traps data read/write bus transfer errors and pre-fetch aborts.</div>
</div>

<div class="func-card isr">
  <div class="func-header">
    <span class="func-name">UsageFault_Handler</span>
    <div class="badges"><span class="badge badge-isr">CPU Fault</span><span class="badge badge-file">stm32f1xx_it.c:130</span></div>
  </div>
  <div class="func-sig">void UsageFault_Handler(void)</div>
  <div class="func-desc">Program fault handler. Catches undefined CPU instructions, unaligned memory access, or divide-by-zero errors.</div>
</div>

<div class="func-card isr">
  <div class="func-header">
    <span class="func-name">SVC_Handler, DebugMon_Handler, PendSV_Handler</span>
    <div class="badges"><span class="badge badge-isr">System ISR</span><span class="badge badge-file">stm32f1xx_it.c:145, 158, 171</span></div>
  </div>
  <div class="func-sig">
    void SVC_Handler(void)<br>
    void DebugMon_Handler(void)<br>
    void PendSV_Handler(void)
  </div>
  <div class="func-desc">Cortex-M3 supervisor call, debug monitor, and pending software interrupt handlers reserved for system operations.</div>
</div>

<h2>4.2 Peripheral Vector Interrupts</h2>
<div class="func-card isr">
  <div class="func-header">
    <span class="func-name">SysTick_Handler</span>
    <div class="badges"><span class="badge badge-isr">Timer ISR</span><span class="badge badge-file">stm32f1xx_it.c:184</span></div>
  </div>
  <div class="func-sig">void SysTick_Handler(void)</div>
  <div class="func-desc">Executes every 1 millisecond on SysTick exception. Calls <code>HAL_IncTick()</code> to maintain HAL tick timing.</div>
</div>

<div class="func-card isr">
  <div class="func-header">
    <span class="func-name">USART1_IRQHandler &amp; USART2_IRQHandler</span>
    <div class="badges"><span class="badge badge-isr">UART ISR</span><span class="badge badge-file">stm32f1xx_it.c:205, 219</span></div>
  </div>
  <div class="func-sig">
    void USART1_IRQHandler(void)<br>
    void USART2_IRQHandler(void)
  </div>
  <div class="func-desc">Dispatches hardware interrupts for USART1 (GPS) and USART2 (Bluetooth) to their respective HAL handlers.</div>
</div>

<!-- ========================================== -->
<!-- 5. RUNTIME, CMSIS & SYSTEM CALLS           -->
<!-- ========================================== -->
<div class="page-break"></div>

<h1>5. System Clock, CMSIS &amp; POSIX System Calls</h1>

<h2>5.1 System Clock Engine (Src/system_stm32f1xx.c)</h2>
<div class="func-card system">
  <div class="func-header">
    <span class="func-name">SystemInit</span>
    <div class="badges"><span class="badge badge-sys">CMSIS</span><span class="badge badge-file">system_stm32f1xx.c:175</span></div>
  </div>
  <div class="func-sig">void SystemInit(void)</div>
  <div class="func-desc">Resets RCC configuration to default state, enables internal HSI oscillator, disables PLL and clock interrupts, and configures the Vector Table Base address.</div>
</div>

<div class="func-card system">
  <div class="func-header">
    <span class="func-name">SystemCoreClockUpdate</span>
    <div class="badges"><span class="badge badge-sys">CMSIS</span><span class="badge badge-file">system_stm32f1xx.c:224</span></div>
  </div>
  <div class="func-sig">void SystemCoreClockUpdate(void)</div>
  <div class="func-desc">Dynamically recalculates the global <code>SystemCoreClock</code> variable (8000000 Hz) based on RCC clock register values.</div>
</div>

<div class="func-card system">
  <div class="func-header">
    <span class="func-name">SystemInit_ExtMemCtl</span>
    <div class="badges"><span class="badge badge-sys">CMSIS</span><span class="badge badge-file">system_stm32f1xx.c:349</span></div>
  </div>
  <div class="func-sig">void SystemInit_ExtMemCtl(void)</div>
  <div class="func-desc">FSMC external memory controller setup stub (unused on medium-density STM32F103C8T6 devices).</div>
</div>

<h2>5.2 Dynamic Memory Management (Src/sysmem.c)</h2>
<div class="func-card system">
  <div class="func-header">
    <span class="func-name">_sbrk</span>
    <div class="badges"><span class="badge badge-sys">Heap</span><span class="badge badge-file">sysmem.c:53</span></div>
  </div>
  <div class="func-sig">void *_sbrk(ptrdiff_t incr)</div>
  <div class="func-desc">Low-level memory allocation engine for C runtime. Extends heap boundary while guarding against collision with the stack pointer (stack overflow guard). Returns <code>(void*)-1</code> on out-of-memory.</div>
</div>

<h2>5.3 POSIX C-Runtime System Calls (Src/syscalls.c)</h2>
<p>
  Implements standard Newlib C library hooks for embedded bare-metal execution:
</p>
<table>
  <thead>
    <tr>
      <th>System Call Function</th>
      <th>Line</th>
      <th>Functional Behavior on Embedded Target</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>__io_putchar(int ch)</code></td><td>35</td><td>Weak symbol redirected to serial UART for character output.</td></tr>
    <tr><td><code>__io_getchar(void)</code></td><td>36</td><td>Weak symbol redirected to serial UART for character input.</td></tr>
    <tr><td><code>initialise_monitor_handles(void)</code></td><td>44</td><td>Initializes semihosting debug stream handles.</td></tr>
    <tr><td><code>_read(int file, char *ptr, int len)</code></td><td>67</td><td>Reads characters using <code>__io_getchar()</code>.</td></tr>
    <tr><td><code>_write(int file, char *ptr, int len)</code></td><td>80</td><td>Writes characters using <code>__io_putchar()</code>.</td></tr>
    <tr><td><code>_close(int file)</code></td><td>92</td><td>Closes file descriptor; returns -1 (no filesystem).</td></tr>
    <tr><td><code>_fstat(int file, struct stat *st)</code></td><td>99</td><td>Populates file status; marks device as character-mode.</td></tr>
    <tr><td><code>_isatty(int file)</code></td><td>106</td><td>Returns 1 (indicates output stream is a TTY terminal).</td></tr>
    <tr><td><code>_lseek(int file, int ptr, int dir)</code></td><td>112</td><td>Repositions file pointer; returns 0.</td></tr>
    <tr><td><code>_open(char *path, int flags, ...)</code></td><td>120</td><td>Opens named file; returns -1 (no file system present).</td></tr>
    <tr><td><code>_wait(int *status)</code></td><td>128</td><td>Waits for child process to terminate; returns -1.</td></tr>
    <tr><td><code>_unlink(char *name)</code></td><td>135</td><td>Removes file entry; returns -1.</td></tr>
    <tr><td><code>_times(struct tms *buf)</code></td><td>142</td><td>Returns elapsed process execution time; returns -1.</td></tr>
    <tr><td><code>_stat(char *file, struct stat *st)</code></td><td>148</td><td>Returns status of a file; returns 0.</td></tr>
    <tr><td><code>_link(char *old, char *new)</code></td><td>155</td><td>Creates file link; returns -1.</td></tr>
    <tr><td><code>_fork(void)</code></td><td>163</td><td>Forks process; returns -1 (unsupported on bare metal).</td></tr>
    <tr><td><code>_execve(...)</code></td><td>169</td><td>Replaces process image; returns -1.</td></tr>
    <tr><td><code>_getpid(void)</code></td><td>48</td><td>Returns process identifier (constant 1).</td></tr>
    <tr><td><code>_kill(int pid, int sig)</code></td><td>53</td><td>Signals process; sets errno=EINVAL and returns -1.</td></tr>
    <tr><td><code>_exit(int status)</code></td><td>61</td><td>Terminates program execution by locking in an infinite loop.</td></tr>
  </tbody>
</table>

<!-- ========================================== -->
<!-- 6. MASTER FUNCTION INDEX TABLE             -->
<!-- ========================================== -->
<div class="page-break"></div>

<h1>6. Master Function Cross-Reference Index</h1>
<p>
  Alphabetical directory of all 46 functions across the entire Smart Cane firmware:
</p>

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Function Name</th>
      <th>Source Module</th>
      <th>Type / Scope</th>
      <th>Role &amp; Responsibility</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>1</td><td><code>BusFault_Handler</code></td><td>stm32f1xx_it.c</td><td>ISR / Trap</td><td>Cortex-M3 Bus Fault Trap</td></tr>
    <tr><td>2</td><td><code>Compute_Lat_Tenths</code></td><td>main.c</td><td>Static Helper</td><td>Converts NMEA latitude to arcminute tenths</td></tr>
    <tr><td>3</td><td><code>Compute_Lon_Tenths</code></td><td>main.c</td><td>Static Helper</td><td>Converts NMEA longitude to arcminute tenths</td></tr>
    <tr><td>4</td><td><code>DebugMon_Handler</code></td><td>stm32f1xx_it.c</td><td>ISR / Trap</td><td>Debug Monitor Exception Handler</td></tr>
    <tr><td>5</td><td><code>Error_Handler</code></td><td>main.c</td><td>Public Trap</td><td>Disables interrupts and halts on error</td></tr>
    <tr><td>6</td><td><code>Filter_And_Send_GPS</code></td><td>main.c</td><td>Public Engine</td><td>Rejects coordinate jumps &gt;1.85 km in 5s</td></tr>
    <tr><td>7</td><td><code>HAL_I2C_MspDeInit</code></td><td>i2c.c</td><td>HAL Callback</td><td>Releases I2C1 GPIOs and clock</td></tr>
    <tr><td>8</td><td><code>HAL_I2C_MspInit</code></td><td>i2c.c</td><td>HAL Callback</td><td>Initializes I2C1 PB6/PB7 pins and clock</td></tr>
    <tr><td>9</td><td><code>HAL_MspInit</code></td><td>stm32f1xx_hal_msp.c</td><td>HAL Core</td><td>Initializes AFIO clock &amp; NVIC Priority Group 4</td></tr>
    <tr><td>10</td><td><code>HAL_TIM_Base_MspDeInit</code></td><td>tim.c</td><td>HAL Callback</td><td>Disables TIM2 clock gate in RCC</td></tr>
    <tr><td>11</td><td><code>HAL_TIM_Base_MspInit</code></td><td>tim.c</td><td>HAL Callback</td><td>Enables TIM2 clock gate in RCC</td></tr>
    <tr><td>12</td><td><code>HAL_UART_MspDeInit</code></td><td>usart.c</td><td>HAL Callback</td><td>Releases USART1/2 GPIOs and NVIC</td></tr>
    <tr><td>13</td><td><code>HAL_UART_MspInit</code></td><td>usart.c</td><td>HAL Callback</td><td>Initializes USART1/2 GPIOs and NVIC</td></tr>
    <tr><td>14</td><td><code>HardFault_Handler</code></td><td>stm32f1xx_it.c</td><td>ISR / Trap</td><td>Fatal Cortex-M3 Hardware Fault Trap</td></tr>
    <tr><td>15</td><td><code>initialise_monitor_handles</code></td><td>syscalls.c</td><td>Runtime Hook</td><td>Semihosting Handle Initializer</td></tr>
    <tr><td>16</td><td><code>main</code></td><td>main.c</td><td>Core Main</td><td>Microcontroller Superloop &amp; Dispatcher</td></tr>
    <tr><td>17</td><td><code>MemManage_Handler</code></td><td>stm32f1xx_it.c</td><td>ISR / Trap</td><td>Memory Protection Unit (MPU) Fault Trap</td></tr>
    <tr><td>18</td><td><code>MX_GPIO_Init</code></td><td>gpio.c</td><td>HAL Driver</td><td>Enables GPIO bus clock gates</td></tr>
    <tr><td>19</td><td><code>MX_I2C1_Init</code></td><td>i2c.c</td><td>HAL Driver</td><td>Configures I2C1 for 100 kHz standard mode</td></tr>
    <tr><td>20</td><td><code>MX_TIM2_Init</code></td><td>tim.c</td><td>HAL Driver</td><td>Configures TIM2 timebase and trigger</td></tr>
    <tr><td>21</td><td><code>MX_USART1_UART_Init</code></td><td>usart.c</td><td>HAL Driver</td><td>Configures USART1 (GPS) for 9600 baud</td></tr>
    <tr><td>22</td><td><code>MX_USART2_UART_Init</code></td><td>usart.c</td><td>HAL Driver</td><td>Configures USART2 (BT) for 9600 baud</td></tr>
    <tr><td>23</td><td><code>NMI_Handler</code></td><td>stm32f1xx_it.c</td><td>ISR / Trap</td><td>Non-Maskable Interrupt Trap</td></tr>
    <tr><td>24</td><td><code>Parse_RMC</code></td><td>main.c</td><td>Public Parser</td><td>Tokenizes $GPRMC/$GNRMC sentences</td></tr>
    <tr><td>25</td><td><code>PendSV_Handler</code></td><td>stm32f1xx_it.c</td><td>ISR / Trap</td><td>Pending Service Call Handler</td></tr>
    <tr><td>26</td><td><code>Process_Emergency_Button</code></td><td>main.c</td><td>Public Engine</td><td>PB1 debounce &amp; 5s cancel state machine</td></tr>
    <tr><td>27</td><td><code>Process_GPS_Byte</code></td><td>main.c</td><td>Public Engine</td><td>Consumes USART1 bytes into sentence buffer</td></tr>
    <tr><td>28</td><td><code>Process_SysTick</code></td><td>main.c</td><td>Public Engine</td><td>1ms software timebase &amp; LED strobe</td></tr>
    <tr><td>29</td><td><code>Process_Ultrasonic</code></td><td>main.c</td><td>Public Engine</td><td>HC-SR04 pulse measurement &amp; alert trigger</td></tr>
    <tr><td>30</td><td><code>Send_Parsed_GPS</code></td><td>main.c</td><td>Public Telemetry</td><td>Transmits human-readable lat/lon to BT</td></tr>
    <tr><td>31</td><td><code>SVC_Handler</code></td><td>stm32f1xx_it.c</td><td>ISR / Trap</td><td>Supervisor Call Handler</td></tr>
    <tr><td>32</td><td><code>SysTick_Handler</code></td><td>stm32f1xx_it.c</td><td>ISR / Timebase</td><td>1ms SysTick interrupt; calls HAL_IncTick</td></tr>
    <tr><td>33</td><td><code>System_Init</code></td><td>main.c</td><td>Public Init</td><td>Bare-metal register initialization</td></tr>
    <tr><td>34</td><td><code>SystemCoreClockUpdate</code></td><td>system_stm32f1xx.c</td><td>CMSIS API</td><td>Recalculates CPU clock frequency</td></tr>
    <tr><td>35</td><td><code>SystemInit</code></td><td>system_stm32f1xx.c</td><td>CMSIS API</td><td>Hardware reset state RCC &amp; vector table</td></tr>
    <tr><td>36</td><td><code>SystemInit_ExtMemCtl</code></td><td>system_stm32f1xx.c</td><td>CMSIS API</td><td>External memory bus controller stub</td></tr>
    <tr><td>37</td><td><code>UART2_Send2DigitNum</code></td><td>main.c</td><td>Public Comm</td><td>Transmits 2-digit distance values over BT</td></tr>
    <tr><td>38</td><td><code>UART2_SendChar</code></td><td>main.c</td><td>Public Comm</td><td>Transmits single character over USART2</td></tr>
    <tr><td>39</td><td><code>UART2_SendNum</code></td><td>main.c</td><td>Public Comm</td><td>Transmits 0-999 decimal integer over BT</td></tr>
    <tr><td>40</td><td><code>UART2_SendString</code></td><td>main.c</td><td>Public Comm</td><td>Transmits null-terminated string over BT</td></tr>
    <tr><td>41</td><td><code>UsageFault_Handler</code></td><td>stm32f1xx_it.c</td><td>ISR / Trap</td><td>Instruction / Alignment CPU Fault Trap</td></tr>
    <tr><td>42</td><td><code>USART1_IRQHandler</code></td><td>stm32f1xx_it.c</td><td>ISR / Comm</td><td>Dispatches USART1 interrupts to HAL</td></tr>
    <tr><td>43</td><td><code>USART2_IRQHandler</code></td><td>stm32f1xx_it.c</td><td>ISR / Comm</td><td>Dispatches USART2 interrupts to HAL</td></tr>
    <tr><td>44</td><td><code>_sbrk</code></td><td>sysmem.c</td><td>Memory Manager</td><td>Heap allocator with stack collision guard</td></tr>
    <tr><td>45</td><td><code>__io_putchar / __io_getchar</code></td><td>syscalls.c</td><td>POSIX Bridge</td><td>Standard I/O character stream hooks</td></tr>
    <tr><td>46</td><td><code>_read / _write / _exit / etc.</code></td><td>syscalls.c</td><td>POSIX System</td><td>Standard C runtime POSIX stubs</td></tr>
  </tbody>
</table>

</body>
</html>
"""

def main():
    workspace_dir = os.path.abspath(os.path.dirname(__file__))
    html_path = os.path.join(workspace_dir, "Smart_Cane_Firmware_Functions_Documentation.html")
    pdf_path = os.path.join(workspace_dir, "Smart_Cane_Firmware_Functions_Documentation.pdf")
    
    print(f"Building HTML report at {html_path}...")
    html_content = build_html()
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Rendering PDF report at {pdf_path} using Microsoft Edge...")
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_path):
        print(f"Error: Edge not found at {edge_path}")
        sys.exit(1)
        
    file_url = "file:///" + html_path.replace("\\", "/")
    cmd = [
        edge_path,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path}",
        "--no-pdf-header-footer",
        file_url
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
        print(f"SUCCESS: Generated PDF ({os.path.getsize(pdf_path)} bytes) at {pdf_path}")
    else:
        print(f"FAILED to generate PDF. Edge stderr: {res.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    main()
