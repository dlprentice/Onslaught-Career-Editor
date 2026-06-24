/* address: 0x005963d2 */
/* name: CDXTexture__Unk_005963d2 */
/* signature: int __fastcall CDXTexture__Unk_005963d2(void * param_1) */


int __fastcall CDXTexture__Unk_005963d2(void *param_1)

{
  float fVar1;
  float fVar2;
  int iVar3;

  iVar3 = 0x10;
  do {
    if (*(float *)((int)param_1 + 0xc) == 0.0) {
      *(float *)param_1 = 0.0;
      *(float *)((int)param_1 + 4) = 0.0;
      fVar1 = 0.0;
LAB_00596444:
      *(float *)((int)param_1 + 8) = fVar1;
    }
    else if (*(float *)((int)param_1 + 0xc) < 1.0) {
      fVar1 = 1.0 / *(float *)((int)param_1 + 0xc);
      if (*(float *)((int)param_1 + 0xc) <= *(float *)param_1) {
        fVar2 = 1.0;
      }
      else {
        fVar2 = fVar1 * *(float *)param_1;
      }
      *(float *)param_1 = fVar2;
      if (*(float *)((int)param_1 + 0xc) <= *(float *)((int)param_1 + 4)) {
        fVar2 = 1.0;
      }
      else {
        fVar2 = fVar1 * *(float *)((int)param_1 + 4);
      }
      *(float *)((int)param_1 + 4) = fVar2;
      if (*(float *)((int)param_1 + 0xc) <= *(float *)((int)param_1 + 8)) {
        fVar1 = 1.0;
      }
      else {
        fVar1 = fVar1 * *(float *)((int)param_1 + 8);
      }
      goto LAB_00596444;
    }
    param_1 = (void *)((int)param_1 + 0x10);
    iVar3 = iVar3 + -1;
    if (iVar3 == 0) {
      return 0;
    }
  } while( true );
}
