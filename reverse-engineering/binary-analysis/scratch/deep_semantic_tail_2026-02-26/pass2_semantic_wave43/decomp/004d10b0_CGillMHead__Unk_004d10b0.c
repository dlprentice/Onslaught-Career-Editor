/* address: 0x004d10b0 */
/* name: CGillMHead__Unk_004d10b0 */
/* signature: void __thiscall CGillMHead__Unk_004d10b0(void * this, int param_1, int param_2) */


void __thiscall CGillMHead__Unk_004d10b0(void *this,int param_1,int param_2)

{
  float fVar1;

  *(undefined4 *)((int)this + 0x10) = 0;
  fVar1 = PLATFORM__GetSysTimeFloat();
  *(float *)((int)this + 0x30) = fVar1;
  if (*(int **)((int)this + 8) != (int *)0x0) {
    (**(code **)(**(int **)((int)this + 8) + 4))(1);
    *(undefined4 *)((int)this + 8) = 0;
  }
  if (*(int **)((int)this + 0x3c) != (int *)0x0) {
    (**(code **)(**(int **)((int)this + 0x3c) + 4))(1);
    *(undefined4 *)((int)this + 0x3c) = 0;
  }
  *(uint *)((int)this + 0x48) = (uint)(param_1 == 0);
  return;
}
