/* address: 0x00595820 */
/* name: CTexture__Helper_00595820 */
/* signature: void __stdcall CTexture__Helper_00595820(void * param_1, void * param_2) */


void CTexture__Helper_00595820(void *param_1,void *param_2)

{
  byte *pbVar1;
  byte *pbVar2;
  byte *pbVar3;
  byte *pbVar4;
  byte *pbVar5;
  byte *pbVar6;
  byte *pbVar7;
  undefined1 uVar8;
  byte bVar9;
  undefined4 *in_EAX;
  int extraout_EAX;
  byte *pbVar10;
  int iVar11;
  uint uVar12;
  int *unaff_EBX;
  uint uVar13;
  undefined4 *puVar14;

  if (*unaff_EBX == 0) {
    CTexture__Helper_0059c650((int)param_1);
    *unaff_EBX = extraout_EAX;
  }
  puVar14 = (undefined4 *)*unaff_EBX;
  *puVar14 = *in_EAX;
  puVar14[1] = in_EAX[1];
  puVar14[2] = in_EAX[2];
  uVar8 = *(undefined1 *)(in_EAX + 4);
  puVar14[3] = in_EAX[3];
  *(undefined1 *)(puVar14 + 4) = uVar8;
  uVar13 = 0;
  pbVar10 = (byte *)((int)in_EAX + 7);
  iVar11 = 2;
  do {
    pbVar1 = pbVar10 + -5;
    pbVar2 = pbVar10 + -6;
    pbVar3 = pbVar10 + -4;
    pbVar4 = pbVar10 + -3;
    pbVar5 = pbVar10 + -2;
    pbVar6 = pbVar10 + -1;
    pbVar7 = pbVar10 + 1;
    bVar9 = *pbVar10;
    pbVar10 = pbVar10 + 8;
    iVar11 = iVar11 + -1;
    uVar13 = bVar9 + uVar13 +
             (uint)*pbVar2 + (uint)*pbVar1 + (uint)*pbVar3 + (uint)*pbVar4 + (uint)*pbVar5 +
             (uint)*pbVar6 + (uint)*pbVar7;
  } while (iVar11 != 0);
  if (((int)uVar13 < 1) || (0x100 < (int)uVar13)) {
    puVar14 = *(undefined4 **)param_1;
    puVar14[5] = 8;
    (*(code *)*puVar14)(param_1);
  }
  iVar11 = *unaff_EBX;
  puVar14 = (undefined4 *)(iVar11 + 0x11);
  for (uVar12 = uVar13 >> 2; uVar12 != 0; uVar12 = uVar12 - 1) {
    *puVar14 = *(undefined4 *)param_2;
    param_2 = (undefined4 *)((int)param_2 + 4);
    puVar14 = puVar14 + 1;
  }
  for (uVar13 = uVar13 & 3; uVar13 != 0; uVar13 = uVar13 - 1) {
    *(undefined1 *)puVar14 = *(undefined1 *)param_2;
    param_2 = (undefined4 *)((int)param_2 + 1);
    puVar14 = (undefined4 *)((int)puVar14 + 1);
  }
  *(undefined4 *)(iVar11 + 0x114) = 0;
  return;
}
