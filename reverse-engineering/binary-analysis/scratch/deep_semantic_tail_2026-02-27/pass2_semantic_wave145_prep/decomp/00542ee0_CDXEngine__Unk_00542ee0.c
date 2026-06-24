/* address: 0x00542ee0 */
/* name: CDXEngine__Unk_00542ee0 */
/* signature: void __thiscall CDXEngine__Unk_00542ee0(void * this, void * param_1, float param_2) */


void __thiscall CDXEngine__Unk_00542ee0(void *this,void *param_1,float param_2)

{
  float10 fVar1;
  float10 fVar2;
  undefined4 local_4;

  fVar1 = (float10)fcos((float10)(float)param_1);
  fVar2 = (float10)fsin((float10)(float)param_1);
  *(float *)this = (float)fVar1;
  *(float *)((int)this + 4) = (float)-fVar2;
  *(undefined4 *)((int)this + 8) = 0;
  *(undefined4 *)((int)this + 0xc) = local_4;
  *(float *)((int)this + 0x10) = (float)fVar2;
  *(float *)((int)this + 0x14) = (float)fVar1;
  *(undefined4 *)((int)this + 0x18) = 0;
  *(undefined4 *)((int)this + 0x1c) = local_4;
  *(undefined4 *)((int)this + 0x20) = 0;
  *(undefined4 *)((int)this + 0x24) = 0;
  *(undefined4 *)((int)this + 0x28) = 0x3f800000;
  *(undefined4 *)((int)this + 0x2c) = local_4;
  return;
}
