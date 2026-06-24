/* address: 0x0059c7cc */
/* name: CDXTexture__InflateInitStateFromHeader */
/* signature: int __stdcall CDXTexture__InflateInitStateFromHeader(int param_1, int param_2, void * param_3, int param_4) */


int CDXTexture__InflateInitStateFromHeader(int param_1,int param_2,void *param_3,int param_4)

{
  int iVar1;

  if (((param_3 == (void *)0x0) || (*(char *)param_3 != '1')) || (param_4 != 0x38)) {
    iVar1 = -6;
  }
  else if (param_1 == 0) {
    iVar1 = -2;
  }
  else {
    *(undefined4 *)(param_1 + 0x18) = 0;
    if (*(int *)(param_1 + 0x20) == 0) {
      *(code **)(param_1 + 0x20) = CTexture__Helper_005b272e;
      *(undefined4 *)(param_1 + 0x28) = 0;
    }
    if (*(int *)(param_1 + 0x24) == 0) {
      *(undefined1 **)(param_1 + 0x24) = &LAB_005b274a;
    }
    iVar1 = (**(code **)(param_1 + 0x20))(*(undefined4 *)(param_1 + 0x28),1,0x18);
    *(int *)(param_1 + 0x1c) = iVar1;
    if (iVar1 == 0) {
      iVar1 = -4;
    }
    else {
      *(undefined4 *)(iVar1 + 0x14) = 0;
      *(undefined4 *)(*(int *)(param_1 + 0x1c) + 0xc) = 0;
      if (param_2 < 0) {
        param_2 = -param_2;
        *(undefined4 *)(*(int *)(param_1 + 0x1c) + 0xc) = 1;
      }
      if ((param_2 < 8) || (0xf < param_2)) {
        iVar1 = -2;
      }
      else {
        *(int *)(*(int *)(param_1 + 0x1c) + 0x10) = param_2;
        iVar1 = CTexture__Helper_005b1e16(param_1);
        *(int *)(*(int *)(param_1 + 0x1c) + 0x14) = iVar1;
        if (*(int *)(*(int *)(param_1 + 0x1c) + 0x14) != 0) {
          CDXTexture__BeginAsyncDecodeJob(param_1);
          return 0;
        }
        iVar1 = -4;
      }
      CDXTexture__FinishAsyncDecodeJob(param_1);
    }
  }
  return iVar1;
}
