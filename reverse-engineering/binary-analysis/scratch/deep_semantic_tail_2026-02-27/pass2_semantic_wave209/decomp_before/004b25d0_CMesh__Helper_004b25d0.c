/* address: 0x004b25d0 */
/* name: CMesh__Helper_004b25d0 */
/* signature: void __thiscall CMesh__Helper_004b25d0(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CMesh__Helper_004b25d0(void *this,int param_1,void *param_2)

{
  float fVar1;
  int iVar2;
  float *pfVar3;
  short *local_1c;
  short *local_18;
  short *local_14;
  float local_10;
  float local_c;
  float local_8;
  undefined4 local_4;

  local_10 = 0.0;
  local_c = 0.0;
  local_8 = 0.0;
  if (*(int *)((int)this + 0x100) == 0) {
    CConsole__Printf(&DAT_0066f580,s_FATAL_ERROR__can_t_get_ranom_ver_0062ffa8);
    *(float *)param_1 = local_10;
    *(float *)(param_1 + 4) = local_c;
    *(float *)(param_1 + 8) = local_8;
    *(undefined4 *)(param_1 + 0xc) = local_4;
    return;
  }
  iVar2 = CPolyBucket__GetRandomTriangle(&local_1c);
  if (iVar2 == 1) {
    iVar2 = Random__NextLCGAbs(DAT_008a9d9c);
    iVar2 = iVar2 % 3;
    if (iVar2 == 0) {
      iVar2 = *(int *)((int)this + 0x100);
      pfVar3 = (float *)(iVar2 + 0x40);
      local_10 = (float)(int)*local_1c * *(float *)(iVar2 + 0x50) * _DAT_005d8618 + *pfVar3;
      local_c = (float)(int)local_1c[1] * *(float *)(iVar2 + 0x50) * _DAT_005d8618 +
                *(float *)(iVar2 + 0x44);
      fVar1 = (float)(int)local_1c[2];
    }
    else if (iVar2 == 1) {
      iVar2 = *(int *)((int)this + 0x100);
      pfVar3 = (float *)(iVar2 + 0x40);
      local_10 = (float)(int)*local_18 * *(float *)(iVar2 + 0x50) * _DAT_005d8618 + *pfVar3;
      local_c = (float)(int)local_18[1] * *(float *)(iVar2 + 0x50) * _DAT_005d8618 +
                *(float *)(iVar2 + 0x44);
      fVar1 = (float)(int)local_18[2];
    }
    else {
      if (iVar2 != 2) goto LAB_004b276f;
      iVar2 = *(int *)((int)this + 0x100);
      pfVar3 = (float *)(iVar2 + 0x40);
      local_10 = (float)(int)*local_14 * *(float *)(iVar2 + 0x50) * _DAT_005d8618 + *pfVar3;
      local_c = (float)(int)local_14[1] * *(float *)(iVar2 + 0x50) * _DAT_005d8618 +
                *(float *)(iVar2 + 0x44);
      fVar1 = (float)(int)local_14[2];
    }
    local_8 = fVar1 * pfVar3[4] * _DAT_005d8618 + pfVar3[2];
  }
LAB_004b276f:
  *(float *)param_1 = local_10;
  *(float *)(param_1 + 4) = local_c;
  *(float *)(param_1 + 8) = local_8;
  *(undefined4 *)(param_1 + 0xc) = local_4;
  return;
}
