/* address: 0x004b1d30 */
/* name: CMeshPart__LinkDamagedPartVariantsBySuffix */
/* signature: void __fastcall CMeshPart__LinkDamagedPartVariantsBySuffix(int param_1) */


void __fastcall CMeshPart__LinkDamagedPartVariantsBySuffix(int param_1)

{
  char cVar1;
  int extraout_EAX;
  int iVar2;
  uint uVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  char *pcVar7;
  char *pcVar8;
  int local_154;
  int local_150 [20];
  char local_100 [256];

  piVar4 = local_150;
  for (iVar2 = 0x14; iVar2 != 0; iVar2 = iVar2 + -1) {
    *piVar4 = 0;
    piVar4 = piVar4 + 1;
  }
  iVar2 = *(int *)(param_1 + 0x128);
  iVar6 = 0;
  local_154 = 0;
  iVar5 = 0;
  if (0 < *(int *)(iVar2 + 0x15c)) {
    do {
      pcVar7 = (char *)(param_1 + 0xdc);
      uVar3 = 0xffffffff;
      pcVar8 = pcVar7;
      do {
        if (uVar3 == 0) break;
        uVar3 = uVar3 - 1;
        cVar1 = *pcVar8;
        pcVar8 = pcVar8 + 1;
      } while (cVar1 != '\0');
      iVar2 = CMCBuggy__Helper_0056e170
                        (pcVar7,(void *)(*(int *)(*(int *)(iVar2 + 0x160) + iVar6 * 4) + 0xdc),
                         (void *)(~uVar3 - 1));
      if (iVar2 == 0) {
        uVar3 = 0xffffffff;
        do {
          if (uVar3 == 0) break;
          uVar3 = uVar3 - 1;
          cVar1 = *pcVar7;
          pcVar7 = pcVar7 + 1;
        } while (cVar1 != '\0');
        pcVar7 = (char *)(~uVar3 + 0xdb +
                         *(int *)(*(int *)(*(int *)(param_1 + 0x128) + 0x160) + iVar6 * 4));
        uVar3 = 0xffffffff;
        pcVar8 = pcVar7;
        do {
          if (uVar3 == 0) break;
          uVar3 = uVar3 - 1;
          cVar1 = *pcVar8;
          pcVar8 = pcVar8 + 1;
        } while (cVar1 != '\0');
        if ((7 < ~uVar3 - 1) &&
           (iVar2 = CMCBuggy__Helper_0056e170(pcVar7,s__damaged_0062ff9c,(void *)0x8), iVar2 == 0))
        {
          uVar3 = 0xffffffff;
          pcVar8 = pcVar7;
          do {
            if (uVar3 == 0) break;
            uVar3 = uVar3 - 1;
            cVar1 = *pcVar8;
            pcVar8 = pcVar8 + 1;
          } while (cVar1 != '\0');
          iVar2 = 1;
          if (8 < ~uVar3 - 1) {
            CSoundManager__Helper_0055e2a6(pcVar7 + 8);
            iVar2 = extraout_EAX;
          }
          if (local_150[iVar2] != 0) {
            sprintf(local_100,s_Duplicate_damage_number_for_part_0062ff74);
          }
          local_150[iVar2] = *(int *)(*(int *)(*(int *)(param_1 + 0x128) + 0x160) + iVar6 * 4);
          local_154 = local_154 + 1;
        }
      }
      iVar2 = *(int *)(param_1 + 0x128);
      iVar6 = iVar6 + 1;
      iVar5 = local_154;
    } while (iVar6 < *(int *)(iVar2 + 0x15c));
  }
  piVar4 = local_150;
  iVar2 = 0x14;
  do {
    iVar6 = *piVar4;
    if (iVar6 != 0) {
      *(int *)(param_1 + 0x9c) = iVar6;
      *(int *)(param_1 + 0xa0) = iVar5;
      *(undefined4 *)(iVar6 + 0xa4) = 1;
      iVar5 = iVar5 + -1;
      param_1 = iVar6;
    }
    piVar4 = piVar4 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return;
}
