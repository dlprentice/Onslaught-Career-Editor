/* address: 0x004a2190 */
/* name: CDXEngine__RenderLandscapeAllocatorStats */
/* signature: void __fastcall CDXEngine__RenderLandscapeAllocatorStats(int param_1) */


void __fastcall CDXEngine__RenderLandscapeAllocatorStats(int param_1)

{
  int iVar1;
  int iVar2;
  bool bVar3;
  void *pvVar4;
  short *psVar5;
  uint uVar6;
  uint *puVar7;
  int iVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  float fVar11;
  undefined4 uVar12;
  undefined4 uVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  int local_27c;
  int local_278;
  int *local_274;
  char local_268 [100];
  uint local_204 [129];

  pvVar4 = CPlatform__Font(&DAT_0088a0a8,2);
  iVar1 = *(int *)((int)pvVar4 + 0x54);
  sprintf(local_268,s_Used___d_bytes_0062f658);
  uVar15 = 0x3f800000;
  uVar14 = 0;
  uVar13 = 0;
  psVar5 = Text__AsciiToWideScratch(local_268);
  uVar12 = 0xffffffff;
  uVar10 = 0x42000000;
  uVar9 = 0x42000000;
  CPlatform__Font(&DAT_0088a0a8,2);
  CDXFont__DrawText(uVar9,uVar10,uVar12,psVar5,uVar13,uVar14,uVar15);
  sprintf(local_268,s_Free___d_bytes_0062f648);
  uVar14 = 0x3f800000;
  uVar13 = 0;
  uVar12 = 0;
  psVar5 = Text__AsciiToWideScratch(local_268);
  fVar11 = (float)(iVar1 + 0x20);
  uVar10 = 0xffffffff;
  uVar9 = 0x42000000;
  CPlatform__Font(&DAT_0088a0a8,2);
  CDXFont__DrawText(uVar9,fVar11,uVar10,psVar5,uVar12,uVar13,uVar14);
  local_27c = iVar1 + 0x20 + iVar1;
  sprintf(local_268,s_Total___d_bytes_0062f6bc);
  uVar14 = 0x3f800000;
  uVar13 = 0;
  uVar12 = 0;
  psVar5 = Text__AsciiToWideScratch(local_268);
  fVar11 = (float)local_27c;
  uVar10 = 0xffffffff;
  uVar9 = 0x42000000;
  CPlatform__Font(&DAT_0088a0a8,2);
  CDXFont__DrawText(uVar9,fVar11,uVar10,psVar5,uVar12,uVar13,uVar14);
  local_27c = local_27c + iVar1;
  local_274 = (int *)(param_1 + 0x10);
  iVar8 = 0;
  do {
    for (iVar2 = local_274[-1]; iVar2 != 0; iVar2 = *(int *)(iVar2 + 0xc)) {
    }
    for (iVar2 = *local_274; iVar2 != 0; iVar2 = *(int *)(iVar2 + 0xc)) {
    }
    sprintf(local_268,s___2d__num_blocks___5d__bytes__8d_0062f668);
    uVar14 = 0x3f800000;
    uVar13 = 0;
    uVar12 = 0;
    psVar5 = Text__AsciiToWideScratch(local_268);
    fVar11 = (float)local_27c;
    uVar10 = 0xffffffff;
    uVar9 = 0x42000000;
    CPlatform__Font(&DAT_0088a0a8,2);
    CDXFont__DrawText(uVar9,fVar11,uVar10,psVar5,uVar12,uVar13,uVar14);
    iVar8 = iVar8 + 2;
    local_27c = local_27c + iVar1;
    local_274 = local_274 + 2;
  } while (iVar8 < 0x10);
  uVar6 = 0;
  puVar7 = local_204;
  do {
    *puVar7 = uVar6;
    uVar6 = uVar6 + 1;
    puVar7 = puVar7 + 1;
  } while (uVar6 < 0x81);
  do {
    bVar3 = false;
    puVar7 = local_204;
    local_278 = 0x80;
    do {
      puVar7 = puVar7 + 1;
      uVar6 = puVar7[-1];
      if (*(int *)(param_1 + 0x58 + uVar6 * 4) < *(int *)(param_1 + 0x58 + *puVar7 * 4)) {
        puVar7[-1] = *puVar7;
        bVar3 = true;
        *puVar7 = uVar6;
      }
      local_278 = local_278 + -1;
    } while (local_278 != 0);
  } while (bVar3);
  iVar8 = 0x81;
  do {
    local_27c = local_27c + iVar1;
    sprintf(local_268,s___32s____15d_bytes____15d_blocks_0062f610);
    uVar14 = 0x3f800000;
    uVar13 = 0;
    uVar12 = 0;
    psVar5 = Text__AsciiToWideScratch(local_268);
    fVar11 = (float)local_27c;
    uVar10 = 0xffffff00;
    uVar9 = 0x42000000;
    CPlatform__Font(&DAT_0088a0a8,2);
    CDXFont__DrawText(uVar9,fVar11,uVar10,psVar5,uVar12,uVar13,uVar14);
    iVar8 = iVar8 + -1;
  } while (iVar8 != 0);
  return;
}
