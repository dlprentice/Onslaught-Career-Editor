/* address: 0x005693e2 */
/* name: CDXTexture__Unk_005693e2 */
/* signature: bool __cdecl CDXTexture__Unk_005693e2(void * param_1, uint param_2) */


bool __cdecl CDXTexture__Unk_005693e2(void *param_1,uint param_2)

{
  BOOL BVar1;

  BVar1 = IsBadReadPtr(param_1,param_2);
  return BVar1 == 0;
}
