/* address: 0x004f7660 */
/* name: CDXBattleLine__TryFlipSharedEdgeForQuality */
/* signature: void __thiscall CDXBattleLine__TryFlipSharedEdgeForQuality(void * this, void * param_1, int param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXBattleLine__TryFlipSharedEdgeForQuality(void *this,void *param_1,int param_2,int param_3)

{
  float *pfVar1;
  float *pfVar2;
  float *pfVar3;
  float *pfVar4;
  int iVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  ushort *puVar9;
  ushort *puVar10;
  uint uVar11;
  uint uVar12;
  int unaff_EDI;

  puVar9 = (ushort *)CDXBattleLine__FindTriangleByDirectedEdge(this,(int)param_1,param_2,unaff_EDI);
  puVar10 = (ushort *)CDXBattleLine__FindTriangleByDirectedEdge(this,param_2,(int)param_1,unaff_EDI)
  ;
  if (puVar9 == (ushort *)0x0) {
    return;
  }
  if (puVar10 == (ushort *)0x0) {
    return;
  }
  iVar5 = *(int *)this;
  uVar12 = (uint)*puVar9;
  uVar11 = (uint)puVar9[1];
  fVar6 = *(float *)(iVar5 + uVar12 * 8) - *(float *)(iVar5 + uVar11 * 8);
  fVar7 = *(float *)(iVar5 + 4 + uVar12 * 8) - *(float *)(iVar5 + 4 + uVar11 * 8);
  pfVar1 = (float *)(iVar5 + uVar12 * 8);
  pfVar2 = (float *)(iVar5 + uVar11 * 8);
  pfVar3 = (float *)(iVar5 + (uint)puVar10[2] * 8);
  fVar6 = SQRT(fVar6 * fVar6 + fVar7 * fVar7);
  pfVar4 = (float *)(iVar5 + (uint)puVar9[2] * 8);
  fVar7 = SQRT((*pfVar4 - *pfVar3) * (*pfVar4 - *pfVar3) +
               (pfVar4[1] - pfVar3[1]) * (pfVar4[1] - pfVar3[1]));
  if (_DAT_005d85f8 <= fVar6 / fVar7) {
    fVar6 = (pfVar3[1] - pfVar2[1]) * (*pfVar4 - *pfVar2) -
            (pfVar4[1] - pfVar2[1]) * (*pfVar3 - *pfVar2);
    fVar7 = (pfVar4[1] - pfVar1[1]) * (*pfVar3 - *pfVar1) -
            (pfVar3[1] - pfVar1[1]) * (*pfVar4 - *pfVar1);
    if (fVar6 <= _DAT_005d856c) {
      return;
    }
    if (fVar7 <= _DAT_005d856c) {
      return;
    }
    if (fVar6 <= fVar7) {
      fVar7 = fVar6 / fVar7;
    }
    else {
      fVar7 = fVar7 / fVar6;
    }
    fVar6 = (pfVar3[1] - pfVar1[1]) * (*pfVar3 - *pfVar2) -
            (*pfVar3 - *pfVar1) * (pfVar3[1] - pfVar2[1]);
    fVar8 = (pfVar4[1] - pfVar1[1]) * (*pfVar4 - *pfVar2) -
            (*pfVar4 - *pfVar1) * (pfVar4[1] - pfVar2[1]);
    if (fVar6 <= fVar8) {
      fVar6 = fVar6 / fVar8;
    }
    else {
      fVar6 = fVar8 / fVar6;
    }
    if (fVar7 <= fVar6) {
      return;
    }
  }
  else {
    if (fVar6 <= fVar7) {
      return;
    }
    if ((pfVar3[1] - pfVar2[1]) * (*pfVar4 - *pfVar2) -
        (pfVar4[1] - pfVar2[1]) * (*pfVar3 - *pfVar2) <= _DAT_005d856c) {
      return;
    }
    if ((pfVar4[1] - pfVar1[1]) * (*pfVar3 - *pfVar1) -
        (pfVar3[1] - pfVar1[1]) * (*pfVar4 - *pfVar1) <= _DAT_005d856c) {
      return;
    }
  }
  *puVar9 = puVar10[2];
  *puVar10 = puVar9[2];
  *(undefined4 *)((int)this + 0x14) = 1;
  return;
}
