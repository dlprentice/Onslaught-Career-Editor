/* address: 0x005891c6 */
/* name: CDXTexture__InitCpuVendorAndSimdFlags */
/* signature: void CDXTexture__InitCpuVendorAndSimdFlags(void) */


/* WARNING: Removing unreachable block (ram,0x005891f0) */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__InitCpuVendorAndSimdFlags(void)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int unaff_EBP;

  CRT__InitSehFrameNoop();
  *(undefined1 **)(unaff_EBP + -0x10) = &stack0xffffffc4;
  *(undefined4 *)(unaff_EBP + -0x14) = 0;
  *(undefined4 *)(unaff_EBP + -0x24) = s_GenuineIntel_005ea2d4._0_4_;
  *(undefined4 *)(unaff_EBP + -0x20) = s_GenuineIntel_005ea2d4._4_4_;
  *(undefined4 *)(unaff_EBP + -0x1c) = s_GenuineIntel_005ea2d4._8_4_;
  *(char *)(unaff_EBP + -0x18) = s_GenuineIntel_005ea2d4[0xc];
  *(undefined4 *)(unaff_EBP + -4) = 0;
  puVar1 = (undefined4 *)cpuid_basic_info(0);
  uVar4 = puVar1[1];
  uVar3 = puVar1[2];
  uVar2 = puVar1[3];
  *(undefined4 *)(unaff_EBP + -0x2c) = *puVar1;
  *(undefined4 *)(unaff_EBP + -0x38) = uVar4;
  *(undefined4 *)(unaff_EBP + -0x34) = uVar3;
  *(undefined4 *)(unaff_EBP + -0x30) = uVar2;
  CDXTexture__DetectCpuSimdFlags();
  return;
}
