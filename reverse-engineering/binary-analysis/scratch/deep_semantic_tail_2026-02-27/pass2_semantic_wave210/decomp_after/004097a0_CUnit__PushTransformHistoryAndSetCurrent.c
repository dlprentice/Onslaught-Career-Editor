/* address: 0x004097a0 */
/* name: CUnit__PushTransformHistoryAndSetCurrent */
/* signature: void __thiscall CUnit__PushTransformHistoryAndSetCurrent(void * this, void * param_1, void * param_2) */


void __thiscall CUnit__PushTransformHistoryAndSetCurrent(void *this,void *param_1,void *param_2)

{
  if (*(int *)((int)this + 0x48) == 0x461c4000) {
    *(undefined4 *)((int)this + 0x80) = *(undefined4 *)param_1;
    *(undefined4 *)((int)this + 0x84) = *(undefined4 *)((int)param_1 + 4);
    *(undefined4 *)((int)this + 0x88) = *(undefined4 *)((int)param_1 + 8);
    *(undefined4 *)((int)this + 0x8c) = *(undefined4 *)((int)param_1 + 0xc);
    *(undefined4 *)((int)this + 0x40) = *(undefined4 *)param_1;
    *(undefined4 *)((int)this + 0x44) = *(undefined4 *)((int)param_1 + 4);
    *(undefined4 *)((int)this + 0x48) = *(undefined4 *)((int)param_1 + 8);
    *(undefined4 *)((int)this + 0x4c) = *(undefined4 *)((int)param_1 + 0xc);
    *(undefined4 *)this = *(undefined4 *)param_1;
    *(undefined4 *)((int)this + 4) = *(undefined4 *)((int)param_1 + 4);
    *(undefined4 *)((int)this + 8) = *(undefined4 *)((int)param_1 + 8);
    *(undefined4 *)((int)this + 0xc) = *(undefined4 *)((int)param_1 + 0xc);
    if (*(int *)((int)this + 0xac) != -0x40800000) {
      *(undefined4 *)((int)this + 0xac) = DAT_00672fd0;
      return;
    }
  }
  else {
    *(undefined4 *)((int)this + 0x40) = *(undefined4 *)this;
    *(undefined4 *)((int)this + 0x44) = *(undefined4 *)((int)this + 4);
    *(undefined4 *)((int)this + 0x48) = *(undefined4 *)((int)this + 8);
    *(undefined4 *)((int)this + 0x4c) = *(undefined4 *)((int)this + 0xc);
    *(undefined4 *)this = *(undefined4 *)param_1;
    *(undefined4 *)((int)this + 4) = *(undefined4 *)((int)param_1 + 4);
    *(undefined4 *)((int)this + 8) = *(undefined4 *)((int)param_1 + 8);
    *(undefined4 *)((int)this + 0xc) = *(undefined4 *)((int)param_1 + 0xc);
    if (*(int *)((int)this + 0xac) != -0x40800000) {
      *(undefined4 *)((int)this + 0xac) = DAT_00672fd0;
    }
  }
  return;
}
