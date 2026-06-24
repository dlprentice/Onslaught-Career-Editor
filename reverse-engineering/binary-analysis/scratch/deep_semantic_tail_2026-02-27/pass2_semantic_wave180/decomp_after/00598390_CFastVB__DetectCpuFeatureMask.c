/* address: 0x00598390 */
/* name: CFastVB__DetectCpuFeatureMask */
/* signature: int CFastVB__DetectCpuFeatureMask(void) */


/* WARNING: Removing unreachable block (ram,0x0059841e) */
/* WARNING: Removing unreachable block (ram,0x0059840c) */
/* WARNING: Removing unreachable block (ram,0x005983e0) */
/* WARNING: Removing unreachable block (ram,0x005983c4) */
/* WARNING: Removing unreachable block (ram,0x005983b9) */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__DetectCpuFeatureMask(void)

{
  char cVar1;
  undefined4 *puVar2;
  uint *puVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  char *pcVar7;
  int *piVar8;
  char local_2c [4];
  char acStack_28 [4];
  char acStack_24 [4];
  char cStack_20;
  int local_1c;
  int local_18;
  int local_14;
  char cStack_10;
  undefined4 local_c;
  uint local_8;

  cStack_10 = s_UnknownVendr_005ef210[0xc];
  local_2c = (char  [4])s_AuthenticAMD_005ef200._0_4_;
  acStack_28 = (char  [4])s_AuthenticAMD_005ef200._4_4_;
  acStack_24 = (char  [4])s_AuthenticAMD_005ef200._8_4_;
  cStack_20 = s_AuthenticAMD_005ef200[0xc];
  cpuid_basic_info(0);
  local_8 = 1;
  piVar8 = (int *)cpuid_basic_info(0);
  local_1c = piVar8[1];
  local_18 = piVar8[2];
  local_14 = piVar8[3];
  if (*piVar8 != 0) {
    puVar2 = (undefined4 *)cpuid_Version_info(1);
    local_c = *puVar2;
    local_8 = -(uint)((puVar2[2] & 0x800000) != 0) & 0x20 | 3 |
              -(uint)((puVar2[2] & 0x2000000) != 0) & 0x40;
    puVar3 = (uint *)cpuid(0x80000000);
    if (0x80000000 < *puVar3) {
      iVar5 = cpuid(0x80000001);
      uVar6 = *(uint *)(iVar5 + 8);
      local_8 = local_8 | 4 | -(uint)((uVar6 & 0x80000000) != 0) & 0x80;
      iVar5 = 0xc;
      pcVar7 = local_2c;
      piVar8 = &local_1c;
      do {
        if (iVar5 == 0) break;
        iVar5 = iVar5 + -1;
        iVar4 = *piVar8;
        cVar1 = *pcVar7;
        pcVar7 = pcVar7 + 1;
        piVar8 = (int *)((int)piVar8 + 1);
      } while (cVar1 == (char)iVar4);
      local_8 = local_8 | -(uint)((uVar6 & 0x40000000) != 0) & 0x100 |
                -(uint)((uVar6 & 0x400000) != 0) & 0x200;
    }
  }
  return local_8;
}
