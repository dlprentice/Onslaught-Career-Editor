/* address: 0x0059361e */
/* name: CDXTexture__GetRenderingIntent */
/* signature: int __stdcall CDXTexture__GetRenderingIntent(int param_1, int param_2, void * param_3) */


int CDXTexture__GetRenderingIntent(int param_1,int param_2,void *param_3)

{
  int iVar1;

  if ((((param_1 == 0) || (param_2 == 0)) || (iVar1 = 0x800, (*(uint *)(param_2 + 8) & 0x800) == 0))
     || (param_3 == (void *)0x0)) {
    iVar1 = 0;
  }
  else {
    *(uint *)param_3 = (uint)*(byte *)(param_2 + 0x2c);
  }
  return iVar1;
}
