/* address: 0x005b3170 */
/* name: CDXTexture__Unk_005b3170 */
/* signature: void __stdcall CDXTexture__Unk_005b3170(void * param_1, int param_2, int param_3, void * param_4) */


void CDXTexture__Unk_005b3170(void *param_1,int param_2,int param_3,void *param_4)

{
  int *piVar1;
  byte bVar2;
  undefined4 *puVar3;
  int iVar4;
  undefined4 uVar5;
  char *pcVar6;
  uint uVar7;
  char cVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  int iVar12;
  int iVar13;
  undefined4 *puVar14;
  int iStack_514;
  int local_510;
  char acStack_508 [260];
  int aiStack_404 [257];

  if ((param_3 < 0) || (3 < param_3)) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0x32;
    puVar3[6] = param_3;
    (*(code *)*puVar3)(param_1);
  }
  if (param_2 == 0) {
    local_510 = *(int *)((int)param_1 + param_3 * 4 + 0x68);
  }
  else {
    local_510 = *(int *)((int)param_1 + param_3 * 4 + 0x58);
  }
  if (local_510 == 0) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0x32;
    puVar3[6] = param_3;
    (*(code *)*puVar3)(param_1);
  }
  if (*(int *)param_4 == 0) {
    uVar5 = (*(code *)**(undefined4 **)((int)param_1 + 4))(param_1,1,0x500);
    *(undefined4 *)param_4 = uVar5;
  }
  iVar4 = *(int *)param_4;
  iVar10 = 0;
  iStack_514 = 1;
  do {
    bVar2 = *(byte *)(iStack_514 + local_510);
    uVar11 = (uint)bVar2;
    if (0x100 < (int)(uVar11 + iVar10)) {
      puVar3 = *(undefined4 **)param_1;
      puVar3[5] = 8;
      (*(code *)*puVar3)(param_1);
    }
    if (uVar11 != 0) {
      cVar8 = (char)iStack_514;
      pcVar6 = acStack_508 + iVar10;
      for (uVar7 = (uint)(bVar2 >> 2); uVar7 != 0; uVar7 = uVar7 - 1) {
        *(uint *)pcVar6 = CONCAT22(CONCAT11(cVar8,cVar8),CONCAT11(cVar8,cVar8));
        pcVar6 = pcVar6 + 4;
      }
      for (uVar7 = uVar11 & 3; uVar7 != 0; uVar7 = uVar7 - 1) {
        *pcVar6 = cVar8;
        pcVar6 = pcVar6 + 1;
      }
      iVar10 = iVar10 + uVar11;
    }
    iStack_514 = iStack_514 + 1;
  } while (iStack_514 < 0x11);
  acStack_508[iVar10] = '\0';
  iVar13 = 0;
  iVar12 = 0;
  iVar9 = (int)acStack_508[0];
  if (acStack_508[0] != '\0') {
    pcVar6 = acStack_508;
    do {
      cVar8 = *pcVar6;
      while (cVar8 == iVar9) {
        cVar8 = acStack_508[iVar12 + 1];
        aiStack_404[iVar12] = iVar13;
        iVar12 = iVar12 + 1;
        iVar13 = iVar13 + 1;
      }
      if (1 << ((byte)iVar9 & 0x1f) <= iVar13) {
        puVar3 = *(undefined4 **)param_1;
        puVar3[5] = 8;
        (*(code *)*puVar3)(param_1);
      }
      pcVar6 = acStack_508 + iVar12;
      iVar13 = iVar13 << 1;
      iVar9 = iVar9 + 1;
    } while (acStack_508[iVar12] != '\0');
  }
  puVar3 = (undefined4 *)(iVar4 + 0x400);
  puVar14 = puVar3;
  for (iVar12 = 0x40; iVar12 != 0; iVar12 = iVar12 + -1) {
    *puVar14 = 0;
    puVar14 = puVar14 + 1;
  }
  iVar12 = 0;
  if (0 < iVar10) {
    do {
      uVar11 = (uint)*(byte *)(local_510 + 0x11 + iVar12);
      if (((int)((-(uint)(param_2 != 0) & 0xffffff10) + 0xff) < (int)uVar11) ||
         (*(char *)((int)puVar3 + uVar11) != '\0')) {
        puVar14 = *(undefined4 **)param_1;
        puVar14[5] = 8;
        (*(code *)*puVar14)(param_1);
      }
      piVar1 = aiStack_404 + iVar12;
      cVar8 = acStack_508[iVar12];
      iVar12 = iVar12 + 1;
      *(int *)(iVar4 + uVar11 * 4) = *piVar1;
      *(char *)((int)puVar3 + uVar11) = cVar8;
    } while (iVar12 < iVar10);
  }
  return;
}
