/* address: 0x005935f2 */
/* name: CDXTexture__Helper_005935f2 */
/* signature: int __stdcall CDXTexture__Helper_005935f2(int param_1, int param_2, void * param_3) */


int CDXTexture__Helper_005935f2(int param_1,int param_2,void *param_3)

{
  int iVar1;

  if ((((param_1 == 0) || (param_2 == 0)) || ((*(byte *)(param_2 + 8) & 1) == 0)) ||
     (param_3 == (void *)0x0)) {
    iVar1 = 0;
  }
  else {
    *(double *)param_3 = (double)*(float *)(param_2 + 0x28);
    iVar1 = 1;
  }
  return iVar1;
}
