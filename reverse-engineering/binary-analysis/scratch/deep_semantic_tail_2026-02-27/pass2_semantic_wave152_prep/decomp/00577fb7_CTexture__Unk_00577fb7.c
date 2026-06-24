/* address: 0x00577fb7 */
/* name: CTexture__Unk_00577fb7 */
/* signature: int __stdcall CTexture__Unk_00577fb7(int param_1, int param_2, int param_3, int param_4, int param_5, float param_6) */


int CTexture__Unk_00577fb7
              (int param_1,int param_2,int param_3,int param_4,int param_5,float param_6)

{
  float fVar1;
  undefined1 local_24 [16];
  undefined1 local_14 [16];

  CTexture__Helper_00577ea4((int)local_24,param_2,param_5,(int)param_6);
  CTexture__Helper_00577ea4((int)local_14,param_3,param_4,(int)param_6);
  fVar1 = (1.0 - param_6) * param_6;
  CTexture__Helper_00577ea4(param_1,(int)local_24,(int)local_14,(int)(fVar1 + fVar1));
  return param_1;
}
