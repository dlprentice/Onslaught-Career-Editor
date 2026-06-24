/* address: 0x00406da0 */
/* name: CBattleEngine__Unk_00406da0 */
/* signature: int CBattleEngine__Unk_00406da0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CBattleEngine__Unk_00406da0(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  int *piVar10;
  bool bVar11;
  int iVar12;
  undefined3 extraout_var;
  undefined4 *puVar13;
  void *in_ECX;
  int *piVar14;
  float *pfVar15;
  int unaff_EDI;
  float *pfVar16;
  float10 fVar17;
  double dVar18;
  void *in_stack_00000004;
  float in_stack_00000008;
  float in_stack_0000000c;
  float in_stack_00000010;
  float in_stack_00000018;
  float local_48;
  int *local_44;
  float fStack_3c;
  float afStack_30 [4];
  float fStack_20;
  float fStack_1c;
  float fStack_18;
  float fStack_10;
  float fStack_c;
  float fStack_8;

  local_48 = 9999999.0;
  local_44 = (int *)0x0;
  DAT_008550d8 = DAT_008550d0;
  if (DAT_008550d0 == (undefined4 *)0x0) {
    piVar14 = (int *)0x0;
  }
  else {
    piVar14 = (int *)*DAT_008550d0;
  }
  if (piVar14 != (int *)0x0) {
    do {
      iVar12 = CBattleEngine__Helper_004fd3d0(in_ECX,piVar14[0x4e],unaff_EDI);
      fVar9 = local_48;
      piVar10 = local_44;
      if ((iVar12 != 0) &&
         (bVar11 = CBattleEngine__Helper_005061f0(in_stack_00000004,(int)piVar14,unaff_EDI),
         CONCAT31(extraout_var,bVar11) != 0)) {
        fVar1 = ((float)piVar14[7] - in_stack_00000008) * ((float)piVar14[7] - in_stack_00000008) +
                ((float)piVar14[8] - in_stack_0000000c) * ((float)piVar14[8] - in_stack_0000000c) +
                ((float)piVar14[9] - in_stack_00000010) * ((float)piVar14[9] - in_stack_00000010);
        fVar17 = (float10)(**(code **)(*piVar14 + 0x16c))();
        fVar17 = ((float10)_DAT_005d8568 - fVar17 * (float10)_DAT_005d85fc) *
                 (float10)in_stack_00000018;
        if (((float10)fVar1 < fVar17 * fVar17) && (fVar1 < local_48)) {
          fVar2 = (float)piVar14[7] - *(float *)((int)in_ECX + 0x1c);
          fVar3 = (float)piVar14[8] - *(float *)((int)in_ECX + 0x20);
          fVar4 = (float)piVar14[9] - *(float *)((int)in_ECX + 0x24);
          pfVar15 = (float *)((int)in_ECX + 0x3c);
          pfVar16 = afStack_30;
          for (iVar12 = 0xc; fVar8 = fStack_10, fVar5 = fStack_20, fVar7 = afStack_30[2],
              fVar6 = afStack_30[1], iVar12 != 0; iVar12 = iVar12 + -1) {
            *pfVar16 = *pfVar15;
            pfVar15 = pfVar15 + 1;
            pfVar16 = pfVar16 + 1;
          }
          fStack_20 = afStack_30[1];
          afStack_30[2] = fStack_10;
          afStack_30[1] = fVar5;
          fStack_10 = fVar7;
          fVar5 = afStack_30[0] * fVar2 + fVar5 * fVar3 + fVar8 * fVar4;
          fStack_3c = fVar6 * fVar2 + fStack_1c * fVar3 + fStack_c * fVar4;
          fVar2 = fVar3 * fStack_18 + fVar7 * fVar2 + fStack_8 * fVar4;
          fVar2 = SQRT(fVar5 * fVar5 + fVar2 * fVar2 + fStack_3c * fStack_3c);
          if (fVar2 != _DAT_005d856c) {
            fStack_3c = (_DAT_005d8568 / fVar2) * fStack_3c;
          }
          dVar18 = CBattleEngine__Helper_00506620((int)in_stack_00000004);
          fVar17 = (float10)fcos((float10)dVar18);
          if (fVar17 < (float10)fStack_3c) {
            puVar13 = CSPtrSet__First((void *)((int)in_ECX + 0x294));
            while ((fVar9 = fVar1, piVar10 = piVar14, puVar13 != (undefined4 *)0x0 &&
                   (fVar9 = local_48, piVar10 = local_44, (int *)*puVar13 != piVar14))) {
              puVar13 = CSPtrSet__Next((void *)((int)in_ECX + 0x294));
            }
          }
        }
      }
      local_44 = piVar10;
      local_48 = fVar9;
      DAT_008550d8 = (undefined4 *)DAT_008550d8[1];
      if (DAT_008550d8 == (undefined4 *)0x0) {
        piVar14 = (int *)0x0;
      }
      else {
        piVar14 = (int *)*DAT_008550d8;
      }
    } while (piVar14 != (int *)0x0);
    return (int)local_44;
  }
  return 0;
}
