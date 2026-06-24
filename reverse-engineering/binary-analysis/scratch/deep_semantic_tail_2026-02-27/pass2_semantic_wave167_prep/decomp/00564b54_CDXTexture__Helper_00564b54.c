/* address: 0x00564b54 */
/* name: CDXTexture__Helper_00564b54 */
/* signature: int __cdecl CDXTexture__Helper_00564b54(int param_1, int param_2, int param_3, int param_4) */


int __cdecl CDXTexture__Helper_00564b54(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  char *pcVar2;

  iVar1 = CTexture__Helper_0056ab1f((void *)param_3,(void *)param_4,&param_4,&param_3);
  if (iVar1 == -1) {
    return -1;
  }
  pcVar2 = CTexture__Helper_0056a936(param_1,param_2,(void *)param_4,param_3);
  CRT__FreeBase(param_4);
  CRT__FreeBase(param_3);
  return (int)pcVar2;
}
