/* address: 0x005acac0 */
/* name: CTexture__Unk_005acac0 */
/* signature: void __stdcall CTexture__Unk_005acac0(void * param_1, int param_2, int param_3, void * param_4) */


void CTexture__Unk_005acac0(void *param_1,int param_2,int param_3,void *param_4)

{
  byte bVar1;
  undefined1 uVar2;
  undefined4 uVar3;
  char *pcVar4;
  int *piVar5;
  uint uVar6;
  undefined1 *puVar7;
  char cVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  undefined4 *puVar17;
  int iStack_524;
  undefined1 *puStack_518;
  int iStack_514;
  uint uStack_510;
  char acStack_508 [256];
  int aiStack_408 [258];

  if ((param_3 < 0) || (3 < param_3)) {
    puVar17 = *(undefined4 **)param_1;
    puVar17[5] = 0x32;
    puVar17[6] = param_3;
    (*(code *)*puVar17)(param_1);
  }
  if (param_2 == 0) {
    iVar11 = *(int *)((int)param_1 + param_3 * 4 + 200);
  }
  else {
    iVar11 = *(int *)((int)param_1 + param_3 * 4 + 0xb8);
  }
  if (iVar11 == 0) {
    puVar17 = *(undefined4 **)param_1;
    puVar17[5] = 0x32;
    puVar17[6] = param_3;
    (*(code *)*puVar17)(param_1);
  }
  if (*(int *)param_4 == 0) {
    uVar3 = (*(code *)**(undefined4 **)((int)param_1 + 4))(param_1,1,0x590);
    *(undefined4 *)param_4 = uVar3;
  }
  iVar14 = *(int *)param_4;
  *(int *)(iVar14 + 0x8c) = iVar11;
  iVar10 = 0;
  iStack_524 = 1;
  do {
    bVar1 = *(byte *)(iStack_524 + iVar11);
    uVar12 = (uint)bVar1;
    if (0x100 < (int)(uVar12 + iVar10)) {
      puVar17 = *(undefined4 **)param_1;
      puVar17[5] = 8;
      (*(code *)*puVar17)(param_1);
    }
    if (uVar12 != 0) {
      cVar8 = (char)iStack_524;
      pcVar4 = acStack_508 + iVar10;
      for (uVar6 = (uint)(bVar1 >> 2); uVar6 != 0; uVar6 = uVar6 - 1) {
        *(uint *)pcVar4 = CONCAT22(CONCAT11(cVar8,cVar8),CONCAT11(cVar8,cVar8));
        pcVar4 = pcVar4 + 4;
      }
      for (uVar6 = uVar12 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
        *pcVar4 = cVar8;
        pcVar4 = pcVar4 + 1;
      }
      iVar10 = iVar10 + uVar12;
    }
    iStack_524 = iStack_524 + 1;
  } while (iStack_524 < 0x11);
  acStack_508[iVar10] = '\0';
  iVar15 = 0;
  iVar13 = 0;
  iVar9 = (int)acStack_508[0];
  if (acStack_508[0] != '\0') {
    pcVar4 = acStack_508;
    do {
      cVar8 = *pcVar4;
      while (cVar8 == iVar9) {
        cVar8 = acStack_508[iVar13 + 1];
        aiStack_408[iVar13 + 1] = iVar15;
        iVar13 = iVar13 + 1;
        iVar15 = iVar15 + 1;
      }
      if (1 << ((byte)iVar9 & 0x1f) <= iVar15) {
        puVar17 = *(undefined4 **)param_1;
        puVar17[5] = 8;
        (*(code *)*puVar17)(param_1);
      }
      pcVar4 = acStack_508 + iVar13;
      iVar15 = iVar15 << 1;
      iVar9 = iVar9 + 1;
    } while (acStack_508[iVar13] != '\0');
  }
  iVar15 = 0;
  iVar13 = 1;
  do {
    if (*(byte *)(iVar13 + iVar11) == 0) {
      *(undefined4 *)(iVar14 + iVar13 * 4) = 0xffffffff;
    }
    else {
      iVar16 = iVar15 - aiStack_408[iVar15 + 1];
      iVar15 = iVar15 + (uint)*(byte *)(iVar13 + iVar11);
      iVar9 = aiStack_408[iVar15];
      *(int *)(iVar14 + 0x48 + iVar13 * 4) = iVar16;
      *(int *)(iVar14 + iVar13 * 4) = iVar9;
    }
    iVar13 = iVar13 + 1;
  } while (iVar13 < 0x11);
  *(undefined4 *)(iVar14 + 0x44) = 0xfffff;
  puVar17 = (undefined4 *)(iVar14 + 0x90);
  for (iVar13 = 0x100; iVar13 != 0; iVar13 = iVar13 + -1) {
    *puVar17 = 0;
    puVar17 = puVar17 + 1;
  }
  iVar13 = 0;
  iStack_514 = 0;
  iVar15 = 1;
  iStack_524 = 7;
  do {
    uStack_510 = (uint)*(byte *)(iVar11 + iVar15);
    if (uStack_510 != 0) {
      iVar9 = 1 << ((byte)iStack_524 & 0x1f);
      puStack_518 = (undefined1 *)(iVar13 + 0x11 + iVar11);
      do {
        iVar16 = aiStack_408[iVar13 + 1] << ((byte)iStack_524 & 0x1f);
        if (0 < iVar9) {
          uVar2 = *puStack_518;
          puVar7 = (undefined1 *)(iVar16 + 0x490 + iVar14);
          piVar5 = (int *)(iVar14 + 0x90 + iVar16 * 4);
          iVar16 = iVar9;
          do {
            *piVar5 = iVar15;
            piVar5 = piVar5 + 1;
            *puVar7 = uVar2;
            puVar7 = puVar7 + 1;
            iVar16 = iVar16 + -1;
            iVar13 = iStack_514;
          } while (iVar16 != 0);
        }
        iVar13 = iVar13 + 1;
        puStack_518 = puStack_518 + 1;
        uStack_510 = uStack_510 - 1;
        iStack_514 = iVar13;
      } while (uStack_510 != 0);
    }
    iVar15 = iVar15 + 1;
    iStack_524 = iStack_524 + -1;
  } while (-1 < iStack_524);
  if ((param_2 != 0) && (iVar14 = 0, 0 < iVar10)) {
    do {
      if (0xf < *(byte *)(iVar11 + 0x11 + iVar14)) {
        puVar17 = *(undefined4 **)param_1;
        puVar17[5] = 8;
        (*(code *)*puVar17)(param_1);
      }
      iVar14 = iVar14 + 1;
    } while (iVar14 < iVar10);
  }
  return;
}
