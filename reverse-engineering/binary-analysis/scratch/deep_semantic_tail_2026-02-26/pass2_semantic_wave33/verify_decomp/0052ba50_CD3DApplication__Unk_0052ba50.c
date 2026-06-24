/* address: 0x0052ba50 */
/* name: CD3DApplication__Unk_0052ba50 */
/* signature: int __thiscall CD3DApplication__Unk_0052ba50(void * this, void * param_1, int param_2) */


int __thiscall CD3DApplication__Unk_0052ba50(void *this,void *param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;

  iVar3 = *(int *)((int)this + 0x32e40) * 0x516c;
  iVar1 = *(int *)((int)this + *(int *)((int)this + 0x32e40) * 0x516c + 0x516c);
  iVar4 = (int)this + iVar1 * 0xf68 + iVar3 + 0x464;
  if (*(void **)((int)this + iVar1 * 0xf68 + iVar3 + 0x59c) == param_1) {
LAB_0052bae1:
    *(void **)(iVar4 + 0xf54) = param_1;
    *(void **)((int)this + 0x32e44) = param_1;
    *(undefined4 *)((int)this + 0x32e4c) = 0;
    (**(code **)(*(int *)this + 0x28))(0);
    iVar3 = CD3DApplication__Initialize3DEnvironment(1);
    if (-1 < iVar3) {
      *(undefined4 *)((int)this + 0x32e4c) = 1;
      return 0;
    }
    iVar3 = CD3DApplication__Unk_0052c4f0(iVar3);
    return iVar3;
  }
  uVar5 = 0;
  if (*(uint *)((int)this + 0x32e3c) != 0) {
    iVar3 = (int)this + 0x464;
    do {
      uVar2 = 0;
      iVar4 = iVar3;
      if (*(int *)(iVar3 + -4) != 0) {
        do {
          if (*(void **)(iVar4 + 0x138) == param_1) {
            *(uint *)((int)this + 0x32e40) = uVar5;
            *(uint *)(iVar3 + 0x4d08) = uVar2;
            goto LAB_0052bae1;
          }
          uVar2 = uVar2 + 1;
          iVar4 = iVar4 + 0xf68;
        } while (uVar2 < *(uint *)(iVar3 + -4));
      }
      uVar5 = uVar5 + 1;
      iVar3 = iVar3 + 0x516c;
    } while (uVar5 < *(uint *)((int)this + 0x32e3c));
  }
  return -0x7fffbffb;
}
