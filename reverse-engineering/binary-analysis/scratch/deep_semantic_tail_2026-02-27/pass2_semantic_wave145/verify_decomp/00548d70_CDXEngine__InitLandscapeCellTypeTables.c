/* address: 0x00548d70 */
/* name: CDXEngine__InitLandscapeCellTypeTables */
/* signature: int __fastcall CDXEngine__InitLandscapeCellTypeTables(void * param_1) */


int __fastcall CDXEngine__InitLandscapeCellTypeTables(void *param_1)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  undefined4 *puVar6;
  char *pcVar7;
  char *pcVar8;
  int *piVar9;
  char *pcVar10;
  undefined4 *local_14;
  int local_10;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  puStack_8 = &LAB_005d7ab2;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  *(undefined4 *)((int)param_1 + 4) = 0;
  *(undefined4 *)((int)param_1 + 8) = 0;
  *(undefined4 *)param_1 = 0;
  local_4 = 0;
  CDXEngine__Helper_004a1390((int)param_1 + 0x214);
  local_4._0_1_ = 1;
  CDXEngine__Helper_004a1390((int)param_1 + 0xae0);
  local_4._0_1_ = 2;
  CDXEngine__Helper_004a1390((int)param_1 + 0x13ac);
  local_4 = CONCAT31(local_4._1_3_,3);
  CDXEngine__Helper_004a1390((int)param_1 + 0x1c78);
  local_10 = 0;
  piVar9 = (int *)((int)param_1 + 0x10);
  for (iVar2 = 0x81; iVar2 != 0; iVar2 = iVar2 + -1) {
    *piVar9 = (int)param_1 + 0x214;
    piVar9 = piVar9 + 1;
  }
  local_14 = &DAT_009c2bcc;
  pcVar7 = (char *)&DAT_009c2dd0;
LAB_00548dfb:
  uVar3 = 0xffffffff;
  pcVar8 = s_Name_not_found_00651040;
  do {
    pcVar10 = pcVar8;
    if (uVar3 == 0) break;
    uVar3 = uVar3 - 1;
    pcVar10 = pcVar8 + 1;
    cVar1 = *pcVar8;
    pcVar8 = pcVar10;
  } while (cVar1 != '\0');
  uVar3 = ~uVar3;
  pcVar8 = pcVar10 + -uVar3;
  pcVar10 = pcVar7;
  for (uVar4 = uVar3 >> 2; iVar2 = DAT_0062e140, uVar4 != 0; uVar4 = uVar4 - 1) {
    *(undefined4 *)pcVar10 = *(undefined4 *)pcVar8;
    pcVar8 = pcVar8 + 4;
    pcVar10 = pcVar10 + 4;
  }
  for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
    *pcVar10 = *pcVar8;
    pcVar8 = pcVar8 + 1;
    pcVar10 = pcVar10 + 1;
  }
  *local_14 = 0xffffffff;
  iVar5 = 0;
  if (iVar2 != 0x81) {
    puVar6 = &DAT_0062e140;
    do {
      if (iVar2 == local_10) {
        uVar3 = 0xffffffff;
        pcVar8 = s_Generic_0062e144 + iVar5 * 0x28;
        goto code_r0x00548e61;
      }
      iVar2 = puVar6[10];
      puVar6 = puVar6 + 10;
      iVar5 = iVar5 + 1;
    } while (iVar2 != 0x81);
  }
  goto LAB_00548e85;
  while( true ) {
    uVar3 = uVar3 - 1;
    pcVar10 = pcVar8 + 1;
    cVar1 = *pcVar8;
    pcVar8 = pcVar10;
    if (cVar1 == '\0') break;
code_r0x00548e61:
    pcVar10 = pcVar8;
    if (uVar3 == 0) break;
  }
  uVar3 = ~uVar3;
  pcVar8 = pcVar10 + -uVar3;
  pcVar10 = pcVar7;
  for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
    *(undefined4 *)pcVar10 = *(undefined4 *)pcVar8;
    pcVar8 = pcVar8 + 4;
    pcVar10 = pcVar10 + 4;
  }
  for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
    *pcVar10 = *pcVar8;
    pcVar8 = pcVar8 + 1;
    pcVar10 = pcVar10 + 1;
  }
  *local_14 = *(undefined4 *)(iVar5 * 0x28 + 0x62e164);
LAB_00548e85:
  pcVar7 = pcVar7 + 0x20;
  local_10 = local_10 + 1;
  local_14 = local_14 + 1;
  if (0x9c3def < (int)pcVar7) {
    ExceptionList = local_c;
    return (int)param_1;
  }
  goto LAB_00548dfb;
}
