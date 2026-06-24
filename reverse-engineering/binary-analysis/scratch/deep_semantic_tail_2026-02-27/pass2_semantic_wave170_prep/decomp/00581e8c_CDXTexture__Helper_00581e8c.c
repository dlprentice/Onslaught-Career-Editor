/* address: 0x00581e8c */
/* name: CDXTexture__Helper_00581e8c */
/* signature: int __thiscall CDXTexture__Helper_00581e8c(void * this, int param_1, int param_2) */


int __thiscall CDXTexture__Helper_00581e8c(void *this,int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  undefined2 in_FPUControlWord;
  double dVar3;
  undefined4 local_c;

  iVar1 = 0;
  if (*(int *)((int)this + 0x14) == 0) {
    local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
    DAT_009d0c58 = local_c;
    if ((*(int *)((int)this + 8) == 1) || (*(int *)((int)this + 8) == 4)) {
      uVar2 = 0;
      if (*(int *)((int)this + 0x1060) != 0) {
        do {
          dVar3 = CFastVB__Helper_005819b8(*(float *)(iVar1 + param_1));
          *(float *)(iVar1 + *(int *)((int)this + 0x1054)) = (float)dVar3;
          dVar3 = CFastVB__Helper_005819b8(*(float *)(iVar1 + 4 + param_1));
          *(float *)(*(int *)((int)this + 0x1054) + 4 + iVar1) = (float)dVar3;
          dVar3 = CFastVB__Helper_005819b8(*(float *)(iVar1 + 8 + param_1));
          *(float *)(*(int *)((int)this + 0x1054) + 8 + iVar1) = (float)dVar3;
          *(undefined4 *)(*(int *)((int)this + 0x1054) + 0xc + iVar1) =
               *(undefined4 *)(iVar1 + 0xc + param_1);
          uVar2 = uVar2 + 1;
          iVar1 = iVar1 + 0x10;
        } while (uVar2 < *(uint *)((int)this + 0x1060));
      }
    }
    else {
      uVar2 = 0;
      if (*(int *)((int)this + 0x1060) != 0) {
        do {
          *(undefined4 *)(iVar1 + *(int *)((int)this + 0x1054)) = *(undefined4 *)(iVar1 + param_1);
          *(undefined4 *)(*(int *)((int)this + 0x1054) + 4 + iVar1) =
               *(undefined4 *)(iVar1 + 4 + param_1);
          *(undefined4 *)(*(int *)((int)this + 0x1054) + 8 + iVar1) =
               *(undefined4 *)(iVar1 + 8 + param_1);
          dVar3 = CFastVB__Helper_005819b8(*(float *)(iVar1 + 0xc + param_1));
          *(float *)(*(int *)((int)this + 0x1054) + 0xc + iVar1) = (float)dVar3;
          uVar2 = uVar2 + 1;
          iVar1 = iVar1 + 0x10;
        } while (uVar2 < *(uint *)((int)this + 0x1060));
      }
    }
  }
  else if ((*(int *)((int)this + 8) == 1) || (*(int *)((int)this + 8) == 4)) {
    uVar2 = 0;
    if (*(int *)((int)this + 0x1060) != 0) {
      do {
        dVar3 = CDXTexture__FastReciprocalSqrtScalar(*(uint *)(iVar1 + param_1));
        *(float *)(iVar1 + *(int *)((int)this + 0x1054)) =
             (float)dVar3 * *(float *)(iVar1 + param_1);
        dVar3 = CDXTexture__FastReciprocalSqrtScalar(*(uint *)(iVar1 + 4 + param_1));
        *(float *)(*(int *)((int)this + 0x1054) + 4 + iVar1) =
             (float)dVar3 * *(float *)(iVar1 + 4 + param_1);
        dVar3 = CDXTexture__FastReciprocalSqrtScalar(*(uint *)(iVar1 + 8 + param_1));
        uVar2 = uVar2 + 1;
        *(float *)(*(int *)((int)this + 0x1054) + 8 + iVar1) =
             (float)dVar3 * *(float *)(iVar1 + 8 + param_1);
        *(undefined4 *)(*(int *)((int)this + 0x1054) + 0xc + iVar1) =
             *(undefined4 *)(iVar1 + 0xc + param_1);
        iVar1 = iVar1 + 0x10;
      } while (uVar2 < *(uint *)((int)this + 0x1060));
    }
  }
  else {
    uVar2 = 0;
    if (*(int *)((int)this + 0x1060) != 0) {
      do {
        *(undefined4 *)(iVar1 + *(int *)((int)this + 0x1054)) = *(undefined4 *)(iVar1 + param_1);
        *(undefined4 *)(*(int *)((int)this + 0x1054) + 4 + iVar1) =
             *(undefined4 *)(iVar1 + 4 + param_1);
        *(undefined4 *)(*(int *)((int)this + 0x1054) + 8 + iVar1) =
             *(undefined4 *)(iVar1 + 8 + param_1);
        dVar3 = CDXTexture__FastReciprocalSqrtScalar(*(uint *)(iVar1 + 0xc + param_1));
        uVar2 = uVar2 + 1;
        *(float *)(*(int *)((int)this + 0x1054) + 0xc + iVar1) =
             (float)dVar3 * *(float *)(iVar1 + 0xc + param_1);
        iVar1 = iVar1 + 0x10;
      } while (uVar2 < *(uint *)((int)this + 0x1060));
    }
  }
  return *(int *)((int)this + 0x1054);
}
