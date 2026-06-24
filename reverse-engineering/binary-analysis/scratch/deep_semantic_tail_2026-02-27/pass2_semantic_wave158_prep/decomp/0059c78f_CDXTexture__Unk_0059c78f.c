/* address: 0x0059c78f */
/* name: CDXTexture__Unk_0059c78f */
/* signature: int __stdcall CDXTexture__Unk_0059c78f(int param_1) */


int CDXTexture__Unk_0059c78f(int param_1)

{
  int iVar1;

  if (((param_1 == 0) || (iVar1 = *(int *)(param_1 + 0x1c), iVar1 == 0)) ||
     (*(int *)(param_1 + 0x24) == 0)) {
    iVar1 = -2;
  }
  else {
    if (*(int *)(iVar1 + 0x14) != 0) {
      CDXTexture__Unk_005b25e0(*(void **)(iVar1 + 0x14),param_1);
    }
    (**(code **)(param_1 + 0x24))(*(undefined4 *)(param_1 + 0x28),*(undefined4 *)(param_1 + 0x1c));
    *(undefined4 *)(param_1 + 0x1c) = 0;
    iVar1 = 0;
  }
  return iVar1;
}
