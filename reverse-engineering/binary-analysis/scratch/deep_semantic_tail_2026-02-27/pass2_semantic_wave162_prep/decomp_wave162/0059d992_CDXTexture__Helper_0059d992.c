/* address: 0x0059d992 */
/* name: CDXTexture__Helper_0059d992 */
/* signature: void __stdcall CDXTexture__Helper_0059d992(void * param_1, int param_2, uint param_3) */


void CDXTexture__Helper_0059d992(void *param_1,int param_2,uint param_3)

{
  if ((((*(uint *)((int)param_1 + 0x58) & 1) == 0) || ((*(uint *)((int)param_1 + 0x58) & 4) == 0))
     && (CDXTexture__Helper_00592d45(param_1,0x5f3c38), param_2 == 0)) {
    return;
  }
  *(uint *)((int)param_1 + 0x58) = *(uint *)((int)param_1 + 0x58) | 0x18;
  if (param_3 != 0) {
    CDXTexture__Helper_00592d63((int)param_1,0x5f3c1c);
  }
  CDXTexture__Helper_0059d614(param_1,param_3);
  return;
}
