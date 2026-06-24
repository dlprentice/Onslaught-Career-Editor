/* address: 0x0055e45f */
/* name: CFastVB__Unk_0055e45f */
/* signature: int __cdecl CFastVB__Unk_0055e45f(int param_1, int param_2, int param_3) */


int __cdecl CFastVB__Unk_0055e45f(int param_1,int param_2,int param_3)

{
  void *pvVar1;
  int iVar2;

  pvVar1 = (void *)CDXTexture__Unk_00564d79();
  if (pvVar1 == (void *)0x0) {
    return 0;
  }
  iVar2 = CFastVB__Helper_00564c09(param_1,(void *)param_2,param_3,pvVar1);
  CRT__UnlockRouteByAddress((uint)pvVar1);
  return iVar2;
}
