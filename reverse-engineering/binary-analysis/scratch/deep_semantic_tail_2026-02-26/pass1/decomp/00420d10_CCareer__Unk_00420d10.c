/* address: 0x00420d10 */
/* name: CCareer__Unk_00420d10 */
/* signature: void __thiscall CCareer__Unk_00420d10(void * this, void * param_1, void * param_2) */


void __thiscall CCareer__Unk_00420d10(void *this,void *param_1,void *param_2)

{
  int iVar1;
  byte bVar2;
  uint uVar3;
  uint uVar4;

  uVar3 = (*(uint *)param_1 ^ *(uint *)this) & 0xffff ^ *(uint *)this;
  *(uint *)this = uVar3;
  uVar4 = (*(uint *)((int)param_1 + 4) & 0x7fff) << 0x10;
  *(uint *)this = uVar4 | uVar3 & 0x8000ffff;
  iVar1 = *(int *)((int)param_1 + 8);
  if (((iVar1 == 0x16) || (iVar1 == 0x15)) || (iVar1 == 0x14)) {
    bVar2 = 1;
  }
  else {
    bVar2 = 0;
  }
  *(uint *)this = (uint)bVar2 << 0x1f | uVar4 | uVar3 & 0xffff;
  return;
}
