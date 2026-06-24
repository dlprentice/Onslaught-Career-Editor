/* address: 0x005b1400 */
/* name: CTexture__Unk_005b1400 */
/* signature: void __fastcall CTexture__Unk_005b1400(int param_1, int param_2, void * param_3) */


void __fastcall CTexture__Unk_005b1400(int param_1,int param_2,void *param_3)

{
  undefined4 *puVar1;
  byte bVar2;
  byte bVar3;
  undefined1 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int *in_EAX;
  undefined1 *puVar11;
  uint uVar12;
  uint uVar13;
  byte *pbVar14;
  byte *pbVar15;
  byte *pbVar16;
  uint uVar17;
  undefined1 *puVar18;
  byte *pbVar19;
  int iVar20;
  int iVar21;

  iVar21 = *(int *)(param_1 + 0x1c8);
  iVar5 = *(int *)(iVar21 + 0x10);
  iVar6 = *(int *)(iVar21 + 0x14);
  iVar7 = *(int *)(iVar21 + 0x18);
  iVar21 = *(int *)(iVar21 + 0x1c);
  iVar8 = *(int *)(param_1 + 0x148);
  uVar17 = *(uint *)(param_1 + 0x70);
  puVar1 = (undefined4 *)(*in_EAX + param_2 * 8);
  pbVar14 = (byte *)*puVar1;
  pbVar15 = (byte *)puVar1[1];
  pbVar19 = *(byte **)(in_EAX[1] + param_2 * 4);
  pbVar16 = *(byte **)(in_EAX[2] + param_2 * 4);
  puVar11 = *(undefined1 **)param_3;
  puVar18 = *(undefined1 **)((int)param_3 + 4);
  for (uVar12 = uVar17 >> 1; uVar12 != 0; uVar12 = uVar12 - 1) {
    bVar2 = *pbVar19;
    bVar3 = *pbVar16;
    pbVar19 = pbVar19 + 1;
    pbVar16 = pbVar16 + 1;
    iVar9 = *(int *)(iVar5 + (uint)bVar3 * 4);
    iVar10 = *(int *)(iVar6 + (uint)bVar2 * 4);
    uVar13 = (uint)*pbVar14;
    iVar20 = *(int *)(iVar21 + (uint)bVar2 * 4) + *(int *)(iVar7 + (uint)bVar3 * 4) >> 0x10;
    *puVar11 = *(undefined1 *)(uVar13 + iVar9 + iVar8);
    puVar11[1] = *(undefined1 *)(uVar13 + iVar20 + iVar8);
    puVar11[2] = *(undefined1 *)(uVar13 + iVar10 + iVar8);
    uVar13 = (uint)pbVar14[1];
    pbVar14 = pbVar14 + 2;
    puVar11[3] = *(undefined1 *)(uVar13 + iVar9 + iVar8);
    puVar11[4] = *(undefined1 *)(uVar13 + iVar20 + iVar8);
    puVar11[5] = *(undefined1 *)(uVar13 + iVar10 + iVar8);
    uVar13 = (uint)*pbVar15;
    puVar11 = puVar11 + 6;
    *puVar18 = *(undefined1 *)(uVar13 + iVar9 + iVar8);
    puVar18[1] = *(undefined1 *)(uVar13 + iVar20 + iVar8);
    puVar18[2] = *(undefined1 *)(uVar13 + iVar10 + iVar8);
    uVar13 = (uint)pbVar15[1];
    pbVar15 = pbVar15 + 2;
    puVar18[3] = *(undefined1 *)(uVar13 + iVar9 + iVar8);
    uVar4 = *(undefined1 *)(uVar13 + iVar20 + iVar8);
    puVar18[5] = *(undefined1 *)(uVar13 + iVar10 + iVar8);
    puVar18[4] = uVar4;
    puVar18 = puVar18 + 6;
  }
  if ((uVar17 & 1) != 0) {
    iVar5 = *(int *)(iVar5 + (uint)*pbVar16 * 4);
    iVar21 = *(int *)(iVar21 + (uint)*pbVar19 * 4);
    iVar7 = *(int *)(iVar7 + (uint)*pbVar16 * 4);
    iVar6 = *(int *)(iVar6 + (uint)*pbVar19 * 4);
    uVar17 = (uint)*pbVar14;
    *puVar11 = *(undefined1 *)(iVar5 + uVar17 + iVar8);
    iVar21 = iVar21 + iVar7 >> 0x10;
    puVar11[1] = *(undefined1 *)(iVar21 + uVar17 + iVar8);
    puVar11[2] = *(undefined1 *)(iVar8 + uVar17 + iVar6);
    uVar17 = (uint)*pbVar15;
    uVar4 = *(undefined1 *)(uVar17 + iVar6 + iVar8);
    *puVar18 = *(undefined1 *)(iVar5 + uVar17 + iVar8);
    puVar18[1] = *(undefined1 *)(iVar21 + uVar17 + iVar8);
    puVar18[2] = uVar4;
  }
  return;
}
