/* address: 0x00596450 */
/* name: CTexture__Helper_00596450 */
/* signature: int __fastcall CTexture__Helper_00596450(void * param_1) */


int __fastcall CTexture__Helper_00596450(void *param_1)

{
  float *in_EAX;
  int iVar1;

  iVar1 = 0x10;
  do {
    *(float *)param_1 = in_EAX[3] * *in_EAX;
    iVar1 = iVar1 + -1;
    *(float *)((int)param_1 + 4) = in_EAX[1] * in_EAX[3];
    *(float *)((int)param_1 + 8) = in_EAX[2] * in_EAX[3];
    *(float *)((int)param_1 + 0xc) = in_EAX[3];
    in_EAX = in_EAX + 4;
    param_1 = (float *)((int)param_1 + 0x10);
  } while (iVar1 != 0);
  return 0;
}
