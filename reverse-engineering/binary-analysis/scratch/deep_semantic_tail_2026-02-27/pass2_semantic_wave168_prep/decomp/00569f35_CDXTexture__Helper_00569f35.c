/* address: 0x00569f35 */
/* name: CDXTexture__Helper_00569f35 */
/* signature: int __cdecl CDXTexture__Helper_00569f35(int param_1, int param_2, int param_3) */


int __cdecl CDXTexture__Helper_00569f35(int param_1,int param_2,int param_3)

{
  uint uVar1;
  bool bVar2;

  InterlockedIncrement(&DAT_009d35f0);
  bVar2 = DAT_009d35ec != 0;
  if (bVar2) {
    InterlockedDecrement(&DAT_009d35f0);
    CRT__LockByIndex(0x13);
  }
  uVar1 = CDXTexture__Helper_00569f92(param_1,(void *)param_2,param_3);
  if (bVar2) {
    CTexture__Helper_005611da(0x13);
  }
  else {
    InterlockedDecrement(&DAT_009d35f0);
  }
  return uVar1;
}
