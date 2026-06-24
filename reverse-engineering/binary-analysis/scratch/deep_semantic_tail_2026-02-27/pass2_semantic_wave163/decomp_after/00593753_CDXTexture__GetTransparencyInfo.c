/* address: 0x00593753 */
/* name: CDXTexture__GetTransparencyInfo */
/* signature: int __stdcall CDXTexture__GetTransparencyInfo(int param_1, int param_2, void * param_3, void * param_4, void * param_5) */


int CDXTexture__GetTransparencyInfo
              (int param_1,int param_2,void *param_3,void *param_4,void *param_5)

{
  int iVar1;

  iVar1 = 0;
  if (((param_1 != 0) && (param_2 != 0)) && ((*(byte *)(param_2 + 8) & 0x10) != 0)) {
    if (*(char *)(param_2 + 0x19) == '\x03') {
      if (param_3 != (void *)0x0) {
        *(undefined4 *)param_3 = *(undefined4 *)(param_2 + 0x30);
        iVar1 = 0x10;
      }
      if (param_5 != (void *)0x0) {
        *(int *)param_5 = param_2 + 0x34;
      }
    }
    else {
      if (param_5 != (void *)0x0) {
        *(int *)param_5 = param_2 + 0x34;
        iVar1 = 0x10;
      }
      if (param_3 != (void *)0x0) {
        *(undefined4 *)param_3 = 0;
      }
    }
    if (param_4 != (void *)0x0) {
      *(uint *)param_4 = (uint)*(ushort *)(param_2 + 0x16);
      iVar1 = 0x10;
    }
  }
  return iVar1;
}
