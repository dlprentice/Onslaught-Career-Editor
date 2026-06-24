/* address: 0x0049bc80 */
/* name: CUnitAI__Unk_0049bc80 */
/* signature: void __thiscall CUnitAI__Unk_0049bc80(void * this, void * param_1, void * param_2) */


void __thiscall CUnitAI__Unk_0049bc80(void *this,void *param_1,void *param_2)

{
  int iVar1;
  float *pfVar2;
  float local_30 [4];
  float local_20;
  float local_1c;
  float local_18;
  float local_10;
  float local_c;
  float local_8;

  local_30[0] = *(float *)((int)this + 0x14) * *(float *)((int)this + 0x28) -
                *(float *)((int)this + 0x18) * *(float *)((int)this + 0x24);
  local_30[1] = -(*(float *)((int)this + 0x10) * *(float *)((int)this + 0x28) -
                 *(float *)((int)this + 0x20) * *(float *)((int)this + 0x18));
  local_30[2] = *(float *)((int)this + 0x10) * *(float *)((int)this + 0x24) -
                *(float *)((int)this + 0x20) * *(float *)((int)this + 0x14);
  local_20 = -(*(float *)((int)this + 4) * *(float *)((int)this + 0x28) -
              *(float *)((int)this + 8) * *(float *)((int)this + 0x24));
  local_1c = *(float *)this * *(float *)((int)this + 0x28) -
             *(float *)((int)this + 0x20) * *(float *)((int)this + 8);
  local_18 = -(*(float *)this * *(float *)((int)this + 0x24) -
              *(float *)((int)this + 0x20) * *(float *)((int)this + 4));
  local_10 = *(float *)((int)this + 0x18) * *(float *)((int)this + 4) -
             *(float *)((int)this + 8) * *(float *)((int)this + 0x14);
  local_c = -(*(float *)((int)this + 0x18) * *(float *)this -
             *(float *)((int)this + 0x10) * *(float *)((int)this + 8));
  local_8 = *(float *)((int)this + 0x14) * *(float *)this -
            *(float *)((int)this + 0x10) * *(float *)((int)this + 4);
  pfVar2 = local_30;
  for (iVar1 = 0xc; iVar1 != 0; iVar1 = iVar1 + -1) {
    *(float *)param_1 = *pfVar2;
    pfVar2 = pfVar2 + 1;
    param_1 = (float *)((int)param_1 + 4);
  }
  return;
}
