/* address: 0x004c8060 */
/* name: CEngine__Unk_004c8060 */
/* signature: int __thiscall CEngine__Unk_004c8060(void * this, int param_1, int param_2, float param_3, float param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CEngine__Unk_004c8060(void *this,int param_1,int param_2,float param_3,float param_4)

{
  void *pvVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int unaff_EDI;
  int iVar7;
  double dVar8;
  double dVar9;
  uint local_18;
  uint local_14;
  int local_c;

  fVar3 = param_3;
  iVar5 = *(int *)((int)this + 0x74);
  if (iVar5 == 0) {
    param_3 = 3.57331e-43;
    local_14 = 0xff;
    local_18 = 0xff;
  }
  else {
    pvVar1 = (void *)((float)param_1 / (float)*(int *)((int)param_3 + 0x80));
    if (*(int *)(iVar5 + 0xa8) == 0) {
      if (*(int *)(iVar5 + 0xa4) == 0) {
        dVar8 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x5c),pvVar1,param_3,unaff_EDI);
        local_c._0_1_ = (byte)(longlong)ROUND(dVar8 * (double)_DAT_005d8c70);
        local_18 = (uint)(byte)local_c;
        dVar8 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 100),pvVar1,param_3,unaff_EDI);
        local_14 = (uint)(longlong)ROUND(dVar8 * (double)_DAT_005d8c70) & 0xff;
        dVar8 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x6c),pvVar1,param_3,unaff_EDI);
        local_c._0_1_ = (byte)(longlong)ROUND(dVar8 * (double)_DAT_005d8c70);
        param_3 = (float)(uint)(byte)local_c;
      }
      else {
        fVar2 = _DAT_005d8568 - (float)pvVar1;
        dVar8 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x5c),pvVar1,param_3,unaff_EDI);
        dVar9 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x74),pvVar1,param_3,unaff_EDI);
        local_14._0_1_ =
             (byte)(longlong)
                   ROUND((dVar9 * (double)(float)pvVar1 + (double)((float)dVar8 * fVar2)) *
                         (double)_DAT_005d8c70);
        local_18 = (uint)(byte)local_14;
        dVar8 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 100),pvVar1,param_3,unaff_EDI);
        dVar9 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x7c),pvVar1,param_3,unaff_EDI);
        local_14 = (uint)(longlong)
                         ROUND((dVar9 * (double)(float)pvVar1 + (double)((float)dVar8 * fVar2)) *
                               (double)_DAT_005d8c70);
        dVar8 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x6c),pvVar1,param_3,unaff_EDI);
        dVar9 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x84),pvVar1,param_3,unaff_EDI);
        local_c._0_1_ =
             (byte)(longlong)
                   ROUND((dVar9 * (double)(float)pvVar1 + (double)((float)dVar8 * fVar2)) *
                         (double)_DAT_005d8c70);
        param_3 = (float)(uint)(byte)local_c;
      }
    }
    else if (*(float *)(iVar5 + 0xac) <= (float)pvVar1) {
      pvVar1 = (void *)(((float)pvVar1 - *(float *)(iVar5 + 0xac)) /
                       (_DAT_005d8568 - *(float *)(iVar5 + 0xac)));
      fVar2 = _DAT_005d8568 - (float)pvVar1;
      dVar8 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x8c),pvVar1,param_3,unaff_EDI);
      dVar9 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x74),pvVar1,param_3,unaff_EDI);
      local_14._0_1_ =
           (byte)(longlong)
                 ROUND((dVar9 * (double)(float)pvVar1 + (double)((float)dVar8 * fVar2)) *
                       (double)_DAT_005d8c70);
      local_18 = (uint)(byte)local_14;
      dVar8 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x94),pvVar1,param_3,unaff_EDI);
      dVar9 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x7c),pvVar1,param_3,unaff_EDI);
      local_14 = (uint)(longlong)
                       ROUND((dVar9 * (double)(float)pvVar1 + (double)((float)dVar8 * fVar2)) *
                             (double)_DAT_005d8c70);
      dVar8 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x9c),pvVar1,param_3,unaff_EDI);
      dVar9 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x84),pvVar1,param_3,unaff_EDI);
      local_c._0_1_ =
           (byte)(longlong)
                 ROUND((dVar9 * (double)(float)pvVar1 + (double)((float)dVar8 * fVar2)) *
                       (double)_DAT_005d8c70);
      param_3 = (float)(uint)(byte)local_c;
    }
    else {
      pvVar1 = (void *)((float)pvVar1 / *(float *)(iVar5 + 0xac));
      fVar2 = _DAT_005d8568 - (float)pvVar1;
      dVar8 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x8c),pvVar1,param_3,unaff_EDI);
      dVar9 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x5c),pvVar1,param_3,unaff_EDI);
      local_14._0_1_ =
           (byte)(longlong)
                 ROUND((dVar9 * (double)fVar2 + (double)((float)dVar8 * (float)pvVar1)) *
                       (double)_DAT_005d8c70);
      local_18 = (uint)(byte)local_14;
      dVar8 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x94),pvVar1,param_3,unaff_EDI);
      dVar9 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 100),pvVar1,param_3,unaff_EDI);
      local_14 = (uint)(longlong)
                       ROUND((dVar9 * (double)fVar2 + (double)((float)dVar8 * (float)pvVar1)) *
                             (double)_DAT_005d8c70);
      dVar8 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x9c),pvVar1,param_3,unaff_EDI);
      dVar9 = CPDSimpleSprite__Helper_004c10c0((void *)(iVar5 + 0x6c),pvVar1,param_3,unaff_EDI);
      local_c._0_1_ =
           (byte)(longlong)
                 ROUND((dVar9 * (double)fVar2 + (double)((float)dVar8 * (float)pvVar1)) *
                       (double)_DAT_005d8c70);
      param_3 = (float)(uint)(byte)local_c;
    }
  }
  if (*(int *)((int)this + 0x90) == 0) {
    iVar5 = *(int *)((int)fVar3 + 0x80) / 2;
    if (iVar5 <= param_1) {
      iVar5 = ((iVar5 - param_1) * 0x11d) / iVar5 + 0xff;
      if (iVar5 < 0) {
        iVar5 = 0;
      }
      local_c = (int)(longlong)ROUND((float)param_2 * _DAT_005d8c70);
      local_c = local_c * iVar5 >> 8;
      goto LAB_004c841c;
    }
  }
  else if ((_DAT_005d8be0 <= *(float *)((int)fVar3 + 0x60)) &&
          (*(float *)((int)fVar3 + 0x60) <= (float)*(int *)((int)this + 0x9c))) {
    local_c = (int)(longlong)
                   ROUND((*(float *)((int)fVar3 + 0x60) / (float)*(int *)((int)this + 0x9c)) *
                         _DAT_005d8c70);
    goto LAB_004c841c;
  }
  local_c = 0xff;
LAB_004c841c:
  iVar4 = (local_14 & 0xff) * local_c;
  iVar6 = (int)(local_18 * local_c + ((int)(local_18 * local_c) >> 0x1f & 0xffU)) >> 8;
  iVar5 = *(int *)((int)this + 100);
  iVar7 = (int)(iVar4 + (iVar4 >> 0x1f & 0xffU)) >> 8;
  iVar4 = (int)((int)param_3 * local_c + ((int)param_3 * local_c >> 0x1f & 0xffU)) >> 8;
  if (iVar5 == 0) {
    return (iVar6 * 0x100 + iVar7) * 0x100 + iVar4;
  }
  if (iVar5 == 1) {
    return ((local_c * 0x100 + local_18) * 0x100 + (local_14 & 0xff)) * 0x100 + (int)param_3;
  }
  if (iVar5 == 2) {
    if (local_c < 0x80) {
      local_c = local_c * 8;
    }
    else {
      local_c = (0xff - local_c) * 2;
    }
    if (0xff < local_c) {
      local_c = 0xff;
    }
    return ((local_c * 0x100 + iVar6) * 0x100 + iVar7) * 0x100 + iVar4;
  }
  return -1;
}
