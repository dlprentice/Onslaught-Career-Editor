/* address: 0x00586a71 */
/* name: CFastVB__Helper_00586a71 */
/* signature: int __thiscall CFastVB__Helper_00586a71(void * this, void * param_1, int param_2) */


int __thiscall CFastVB__Helper_00586a71(void *this,void *param_1,int param_2)

{
  uint uVar1;
  void *extraout_EAX;
  void *pvVar2;
  uint uVar3;
  int iVar4;

  CFastVB__Helper_00581a4f();
  uVar3 = *(uint *)((int)this + 0x1038) & 0xfffffffe;
  uVar1 = *(int *)((int)this + 0x1040) + 1U & 0xfffffffe;
  iVar4 = uVar1 - uVar3;
  *(uint *)((int)this + 0x1080) = uVar1;
  *(undefined ***)this = &PTR_LAB_005ea138;
  *(uint *)((int)this + 0x1078) = uVar3;
  *(undefined4 *)((int)this + 0x107c) = 0;
  *(undefined4 *)((int)this + 0x1088) = 0;
  *(undefined4 *)((int)this + 0x1084) = 0;
  *(undefined4 *)((int)this + 0x108c) = 0;
  *(int *)((int)this + 0x1090) = iVar4;
  *(undefined4 *)((int)this + 0x1094) = 0;
  *(undefined4 *)((int)this + 0x1098) = 1;
  CFastVB__Helper_00426fd0(iVar4 * 0x10);
  if (extraout_EAX == (void *)0x0) {
    pvVar2 = (void *)0x0;
  }
  else {
    _vector_constructor_iterator_(extraout_EAX,0x10,iVar4,CFastVB__Helper_00574577);
    pvVar2 = extraout_EAX;
  }
  *(void **)((int)this + 0x1074) = pvVar2;
  if (pvVar2 == (void *)0x0) {
    *(undefined4 *)((int)this + 0x1098) = 0;
  }
  iVar4 = *(int *)((int)param_1 + 4);
  if (iVar4 == 0x32595559) {
LAB_00586b4a:
    *(undefined4 *)((int)this + 0x109c) = 0;
    *(undefined4 *)((int)this + 0x10a0) = 8;
  }
  else {
    if (iVar4 != 0x42475247) {
      if (iVar4 == 0x47424752) goto LAB_00586b4a;
      if (iVar4 != 0x59565955) {
        return (int)this;
      }
    }
    *(undefined4 *)((int)this + 0x109c) = 8;
    *(undefined4 *)((int)this + 0x10a0) = 0;
  }
  return (int)this;
}
