/* address: 0x004f7ab0 */
/* name: CUMTexture__ConfigureByMode */
/* signature: void __thiscall CUMTexture__ConfigureByMode(void * this, void * param_1, int param_2, int param_3, int param_4) */


void __thiscall
CUMTexture__ConfigureByMode(void *this,void *param_1,int param_2,int param_3,int param_4)

{
  *(void **)((int)this + 0x14) = param_1;
  *(int *)((int)this + 0x18) = param_3;
  if (param_2 == 0) {
    *(undefined4 *)((int)this + 0xc) = 0x17;
    *(undefined4 *)((int)this + 0x10) = 1;
    *(undefined4 *)((int)this + 0x1c) = 0;
    (**(code **)(*(int *)this + 8))();
    return;
  }
  if (param_2 == 3) {
    *(undefined4 *)((int)this + 0xc) = 0;
    *(undefined4 *)((int)this + 0x10) = 1;
    *(undefined4 *)((int)this + 0x1c) = 0;
    (**(code **)(*(int *)this + 8))();
    return;
  }
  if (param_2 == 1) {
    *(undefined4 *)((int)this + 0xc) = 0x17;
    *(undefined4 *)((int)this + 0x10) = 0;
    if (DAT_006fabcc == 0) {
      *(undefined4 *)((int)this + 0x1c) = 0;
      (**(code **)(*(int *)this + 8))();
      return;
    }
  }
  else {
    if (param_2 == 4) {
      *(undefined4 *)((int)this + 0xc) = 0x15;
      *(undefined4 *)((int)this + 0x10) = 0;
      *(undefined4 *)((int)this + 0x1c) = 1;
      (**(code **)(*(int *)this + 8))();
      return;
    }
    if (param_2 != 5) goto LAB_004f7b51;
    *(undefined4 *)((int)this + 0xc) = 0x17;
    *(undefined4 *)((int)this + 0x10) = 0;
  }
  *(undefined4 *)((int)this + 0x1c) = 1;
LAB_004f7b51:
  (**(code **)(*(int *)this + 8))();
  return;
}
