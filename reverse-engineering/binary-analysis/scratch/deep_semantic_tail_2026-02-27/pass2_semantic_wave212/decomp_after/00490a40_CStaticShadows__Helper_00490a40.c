/* address: 0x00490a40 */
/* name: CStaticShadows__Helper_00490a40 */
/* signature: int __thiscall CStaticShadows__Helper_00490a40(void * this, int param_1, int param_2, void * param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall
CStaticShadows__Helper_00490a40(void *this,int param_1,int param_2,void *param_3,int param_4)

{
  float fVar1;
  undefined4 uVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  int iVar6;
  int iVar7;
  int unaff_EDI;
  double dVar8;
  float local_84;
  int local_74;
  float local_60;
  float local_5c;
  float local_58;
  float local_50;
  float local_4c;
  float local_48;
  undefined **local_40 [5];
  float local_2c;
  float local_28;
  float local_24;
  float local_1c;
  float local_18;
  float local_14;
  undefined4 local_10;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d3188;
  local_c = ExceptionList;
  fVar1 = *(float *)((int)this + 0x1034);
  local_74 = 0xb;
  local_48 = *(float *)(param_1 + 0x2c) - *(float *)(param_1 + 0x1c);
  local_4c = *(float *)(param_1 + 0x28) - *(float *)(param_1 + 0x18);
  local_50 = *(float *)(param_1 + 0x24) - *(float *)(param_1 + 0x14);
  fVar4 = local_48 * local_48 + local_4c * local_4c + local_50 * local_50;
  fVar5 = SQRT(fVar4);
  local_84 = fVar5 * _DAT_005d8c1c;
  ExceptionList = &local_c;
  if (_DAT_005d8ba0 < local_84) {
    local_84 = 2.0;
    ExceptionList = &local_c;
    dVar8 = CRT__RoundDoubleWithFpuChecks((double)(fVar5 * _DAT_005d85ec));
    local_74 = (int)(longlong)ROUND(dVar8);
    local_74 = local_74 + 1;
  }
  fVar4 = SQRT(fVar4);
  if (fVar4 != _DAT_005d856c) {
    fVar4 = _DAT_005d8568 / fVar4;
    local_50 = fVar4 * local_50;
    local_4c = fVar4 * local_4c;
    local_48 = fVar4 * local_48;
  }
  uVar2 = *(undefined4 *)(param_1 + 0x20);
  local_60 = *(float *)(param_1 + 0x14);
  local_5c = *(float *)(param_1 + 0x18);
  local_58 = *(float *)(param_1 + 0x1c);
  iVar7 = 0;
  if (-1 < local_74) {
    do {
      if ((param_3 == (void *)0x1) && (fVar1 <= local_58)) goto LAB_00490cb3;
      fVar4 = (local_60 - _DAT_005dc244) + _DAT_005dbdec;
      fVar5 = (local_5c - _DAT_005dc244) + _DAT_005dbdec;
      fVar3 = _DAT_005d856c;
      if ((((uint)fVar5 | (uint)fVar4) & 0x3e0000) == 0) {
        iVar6 = ((int)fVar5 >> 5 & 0xfc0U) + ((int)fVar4 >> 0xb & 0x3fU);
        if (*(float *)((int)this + iVar6 * 8 + 0x13e0) <= local_58) {
          if (*(float *)((int)this + iVar6 * 8 + 0x13dc) < local_58) goto LAB_00490cb3;
          fVar3 = *(float *)((int)this + 0x102c);
          iVar6 = CHeightField__SampleInterpolatedHeight((int)this,(uint)fVar4,(uint)fVar5);
          fVar3 = (float)(int)(short)iVar6 * fVar3;
          goto joined_r0x00490c77;
        }
      }
      else {
joined_r0x00490c77:
        if (fVar3 < local_58) {
LAB_00490cb3:
          if (local_84 <= _DAT_005d8574) {
            *(float *)param_2 = local_60;
            *(float *)(param_2 + 4) = local_5c;
            *(float *)(param_2 + 8) = local_58;
            *(undefined4 *)(param_2 + 0xc) = uVar2;
            ExceptionList = local_c;
            return 1;
          }
          Vec3__SetXYZ();
          local_1c = local_60;
          local_18 = local_5c;
          local_40[0] = &PTR_VFuncSlot_00_00426340_005d8bfc;
          local_4 = 0;
          local_2c = local_60 - local_50 * local_84;
          local_28 = local_5c - local_4c * local_84;
          local_24 = local_58 - local_48 * local_84;
          local_14 = local_58;
          local_10 = uVar2;
          iVar7 = CStaticShadows__Helper_00490a40(this,(int)local_40,param_2,param_3,unaff_EDI);
          if (iVar7 != 0) {
            ExceptionList = local_c;
            return iVar7;
          }
          CConsole__Printf(&DAT_0066f580,s_Warning__LOS_return_FALSE_in_low_0062d964);
          *(float *)param_2 = local_60;
          *(float *)(param_2 + 4) = local_5c;
          *(float *)(param_2 + 8) = local_58;
          *(undefined4 *)(param_2 + 0xc) = uVar2;
          ExceptionList = local_c;
          return 1;
        }
      }
      local_60 = local_60 + local_50 * local_84;
      iVar7 = iVar7 + 1;
      local_5c = local_5c + local_4c * local_84;
      local_58 = local_48 * local_84 + local_58;
    } while (iVar7 <= local_74);
  }
  ExceptionList = local_c;
  return 0;
}
