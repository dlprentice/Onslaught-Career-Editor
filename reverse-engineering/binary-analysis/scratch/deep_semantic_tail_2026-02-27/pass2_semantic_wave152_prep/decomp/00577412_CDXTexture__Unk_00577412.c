/* address: 0x00577412 */
/* name: CDXTexture__Unk_00577412 */
/* signature: void __stdcall CDXTexture__Unk_00577412(void * param_1, float param_2) */


void CDXTexture__Unk_00577412(void *param_1,float param_2)

{
  float10 fVar1;
  float10 fVar2;

  fVar1 = (float10)fcos((float10)param_2);
  fVar2 = (float10)fsin((float10)param_2);
  *(float *)param_1 = (float)fVar1;
  *(float *)((int)param_1 + 4) = (float)fVar2;
  *(undefined4 *)((int)param_1 + 8) = 0;
  *(undefined4 *)((int)param_1 + 0xc) = 0;
  *(float *)((int)param_1 + 0x10) = -(float)fVar2;
  *(float *)((int)param_1 + 0x14) = (float)fVar1;
  *(undefined4 *)((int)param_1 + 0x18) = 0;
  *(undefined4 *)((int)param_1 + 0x1c) = 0;
  *(undefined4 *)((int)param_1 + 0x20) = 0;
  *(undefined4 *)((int)param_1 + 0x24) = 0;
  *(undefined4 *)((int)param_1 + 0x28) = 0x3f800000;
  *(undefined4 *)((int)param_1 + 0x2c) = 0;
  *(undefined4 *)((int)param_1 + 0x30) = 0;
  *(undefined4 *)((int)param_1 + 0x34) = 0;
  *(undefined4 *)((int)param_1 + 0x38) = 0;
  *(undefined4 *)((int)param_1 + 0x3c) = 0x3f800000;
  return;
}
