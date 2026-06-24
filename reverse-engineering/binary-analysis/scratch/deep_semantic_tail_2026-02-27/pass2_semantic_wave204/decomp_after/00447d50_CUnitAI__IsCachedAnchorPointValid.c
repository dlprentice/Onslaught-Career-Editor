/* address: 0x00447d50 */
/* name: CUnitAI__IsCachedAnchorPointValid */
/* signature: int __fastcall CUnitAI__IsCachedAnchorPointValid(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CUnitAI__IsCachedAnchorPointValid(void *param_1)

{
  float *pfVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  float10 fVar11;
  float10 fVar12;
  float10 fVar13;
  float10 fVar14;
  double dVar15;
  uint uStack_10;
  int iStack_c;

  pfVar1 = (float *)((int)param_1 + 0x280);
  fVar11 = (float10)(**(code **)(*(int *)param_1 + 0x40))();
  iVar5 = CMapWho__GetFirstEntryWithinRadius
                    (*pfVar1,*(undefined4 *)((int)param_1 + 0x284),
                     *(undefined4 *)((int)param_1 + 0x288),*(undefined4 *)((int)param_1 + 0x28c),
                     (float)(fVar11 + fVar11));
  iVar4 = DAT_00855298;
  while (DAT_00855298 = iVar4, iVar5 != 0) {
    piVar6 = (int *)CMapWhoEntry__GetOwner();
    if (((*(byte *)(piVar6 + 0xd) & 0x10) != 0) && (piVar6 != param_1)) {
      dVar15 = CStaticShadows__Helper_0047eb80(0x6fadc8,piVar6 + 7);
      if (dVar15 - (double)(float)piVar6[9] < (double)_DAT_005d85d8) {
        fVar2 = (float)piVar6[7] - *pfVar1;
        fVar3 = (float)piVar6[8] - *(float *)((int)param_1 + 0x284);
        fVar11 = (float10)(**(code **)(*(int *)param_1 + 0x40))();
        fVar12 = (float10)(**(code **)(*(int *)param_1 + 0x40))();
        fVar13 = (float10)(**(code **)(*piVar6 + 0x40))();
        fVar14 = (float10)(**(code **)(*piVar6 + 0x40))();
        uStack_10 = (uint)((float10)(fVar2 * fVar2 + fVar3 * fVar3) <=
                          fVar14 * (float10)(float)fVar13 +
                          (float10)(float)(fVar12 * (float10)(float)fVar11));
        if ((float)uStack_10 + _DAT_005db254 != _DAT_005d856c) {
          return 0;
        }
      }
    }
    iVar5 = CMapWho__GetNextEntryWithinRadius();
    iVar4 = DAT_00855298;
  }
  if ((*(int *)((int)param_1 + 0x27c) != 2) && (*(int *)((int)param_1 + 0x27c) != 3)) {
    fVar11 = (float10)(**(code **)(*(int *)param_1 + 0x40))();
    iStack_c = (int)(longlong)ROUND(fVar11);
    iVar10 = iStack_c + 3 >> 1;
    iStack_c = (int)(longlong)ROUND(*pfVar1);
    iVar9 = iStack_c >> 1;
    iStack_c = (int)(longlong)ROUND(*(float *)((int)param_1 + 0x284));
    for (iVar5 = (iStack_c >> 1) - iVar10; iVar5 < (iStack_c >> 1) + iVar10; iVar5 = iVar5 + 1) {
      if (((-1 < iVar5) && (iVar5 < 0x100)) && (uVar7 = iVar9 - iVar10, (int)uVar7 < iVar9 + iVar10)
         ) {
        do {
          if ((-1 < (int)uVar7) && ((int)uVar7 < 0x100)) {
            uVar8 = uVar7 & 0x80000007;
            if ((int)uVar8 < 0) {
              uVar8 = (uVar8 - 1 | 0xfffffff8) + 1;
            }
            if ((*(byte *)(((int)uVar7 >> 3) * 0x100 + iVar5 + iVar4) &
                (byte)(1 << ((byte)uVar8 & 0x1f))) == 0) {
              return 0;
            }
          }
          uVar7 = uVar7 + 1;
        } while ((int)uVar7 < iVar9 + iVar10);
      }
    }
  }
  return 1;
}
