/* address: 0x004f74b0 */
/* name: CDXBattleLine__SplitTriangleAtPointAndLegalizeEdges */
/* signature: int __thiscall CDXBattleLine__SplitTriangleAtPointAndLegalizeEdges(void * this, void * param_1, void * param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall
CDXBattleLine__SplitTriangleAtPointAndLegalizeEdges
          (void *this,void *param_1,void *param_2,void *param_3)

{
  ushort uVar1;
  int iVar2;
  undefined4 uVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  int iVar10;
  void *pvVar11;
  void *pvVar12;
  int unaff_EDI;
  uint uVar13;
  void *pvVar14;

  if (*(int *)((int)this + 8) < *(int *)((int)this + 0x10)) {
    iVar10 = *(int *)this;
    fVar4 = *(float *)(iVar10 + (uint)*(ushort *)param_1 * 8) - *(float *)param_2;
    fVar5 = *(float *)(iVar10 + (uint)*(ushort *)param_1 * 8 + 4) - *(float *)((int)param_2 + 4);
    uVar13 = (uint)*(ushort *)((int)param_1 + 2);
    fVar8 = *(float *)(iVar10 + uVar13 * 8) - *(float *)param_2;
    uVar1 = *(ushort *)((int)param_1 + 4);
    pvVar14 = (void *)CONCAT22((short)(iVar10 + uVar13 * 8 >> 0x10),uVar1);
    fVar9 = *(float *)(iVar10 + 4 + uVar13 * 8) - *(float *)((int)param_2 + 4);
    fVar6 = *(float *)(iVar10 + (uint)uVar1 * 8) - *(float *)param_2;
    fVar7 = *(float *)(iVar10 + (uint)uVar1 * 8 + 4) - *(float *)((int)param_2 + 4);
    if (((_DAT_005d856c <= fVar9 * fVar4 - fVar5 * fVar8) &&
        (_DAT_005d856c <= fVar7 * fVar8 - fVar6 * fVar9)) &&
       (_DAT_005d856c <= fVar6 * fVar5 - fVar7 * fVar4)) {
      *(undefined2 *)((int)param_1 + 4) = *(undefined2 *)((int)this + 8);
      *(ushort *)(*(int *)((int)this + 4) + *(int *)((int)this + 0xc) * 6) =
           *(ushort *)((int)param_1 + 2);
      *(ushort *)(*(int *)((int)this + 4) + 2 + *(int *)((int)this + 0xc) * 6) = uVar1;
      *(undefined2 *)(*(int *)((int)this + 4) + 4 + *(int *)((int)this + 0xc) * 6) =
           *(undefined2 *)((int)this + 8);
      iVar10 = *(int *)((int)this + 0xc) + 1;
      *(int *)((int)this + 0xc) = iVar10;
      *(ushort *)(*(int *)((int)this + 4) + iVar10 * 6) = uVar1;
      *(undefined2 *)(*(int *)((int)this + 4) + 2 + *(int *)((int)this + 0xc) * 6) =
           *(undefined2 *)param_1;
      *(undefined2 *)(*(int *)((int)this + 4) + 4 + *(int *)((int)this + 0xc) * 6) =
           *(undefined2 *)((int)this + 8);
      iVar10 = *(int *)((int)this + 8);
      iVar2 = *(int *)this;
      *(int *)((int)this + 0xc) = *(int *)((int)this + 0xc) + 1;
      uVar3 = *(undefined4 *)param_2;
      *(undefined4 *)(iVar2 + iVar10 * 8) = uVar3;
      *(undefined4 *)(iVar2 + 4 + iVar10 * 8) = *(undefined4 *)((int)param_2 + 4);
      iVar10 = *(int *)((int)this + 8) + 1;
      *(int *)((int)this + 8) = iVar10;
      pvVar12 = (void *)CONCAT22((short)((uint)uVar3 >> 0x10),*(undefined2 *)((int)param_1 + 2));
      pvVar11 = (void *)CONCAT22((short)((uint)iVar10 >> 0x10),*(undefined2 *)param_1);
      CDXBattleLine__TryFlipSharedEdgeForQuality(this,pvVar11,(int)pvVar12,unaff_EDI);
      CDXBattleLine__TryFlipSharedEdgeForQuality(this,pvVar12,(int)pvVar14,unaff_EDI);
      CDXBattleLine__TryFlipSharedEdgeForQuality(this,pvVar14,(int)pvVar11,unaff_EDI);
      return 1;
    }
  }
  return 0;
}
