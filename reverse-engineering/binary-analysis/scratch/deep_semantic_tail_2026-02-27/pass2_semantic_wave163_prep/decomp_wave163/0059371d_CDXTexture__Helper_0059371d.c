/* address: 0x0059371d */
/* name: CDXTexture__Helper_0059371d */
/* signature: int __stdcall CDXTexture__Helper_0059371d(int param_1, int param_2, void * param_3, void * param_4) */


int CDXTexture__Helper_0059371d(int param_1,int param_2,void *param_3,void *param_4)

{
  int iVar1;

  if ((((param_1 == 0) || (param_2 == 0)) || ((*(byte *)(param_2 + 8) & 8) == 0)) ||
     (param_3 == (void *)0x0)) {
    iVar1 = 0;
  }
  else {
    *(undefined4 *)param_3 = *(undefined4 *)(param_2 + 0x10);
    *(uint *)param_4 = (uint)*(ushort *)(param_2 + 0x14);
    iVar1 = 8;
  }
  return iVar1;
}
