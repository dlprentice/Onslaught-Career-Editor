/* address: 0x005693fe */
/* name: CDXTexture__Unk_005693fe */
/* signature: bool __cdecl CDXTexture__Unk_005693fe(int param_1, uint param_2) */


bool __cdecl CDXTexture__Unk_005693fe(int param_1,uint param_2)

{
  BOOL BVar1;

  BVar1 = IsBadWritePtr((LPVOID)param_1,param_2);
  return BVar1 == 0;
}
