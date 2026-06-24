/* address: 0x00587477 */
/* name: CFastVB__Helper_00587477 */
/* signature: int __thiscall CFastVB__Helper_00587477(void * this, void * param_1, int param_2) */


int __thiscall CFastVB__Helper_00587477(void *this,void *param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint *puVar4;
  uint uVar5;
  uint *puVar6;
  uint uVar7;

  CFastVB__TexelUnpackProfile__ctorFromDescriptor();
  iVar2 = *(int *)((int)this + 4);
  *(undefined ***)this = &PTR_CFastVB__TexelCodecProfile_scalar_deleting_dtor_005e9ee4;
  if (iVar2 == 0x31545844) {
    *(undefined4 *)((int)this + 0x107c) = 8;
    *(code **)((int)this + 0x1084) = CTexture__Helper_00597949;
    *(code **)((int)this + 0x1080) = CDXTexture__DecodeDxt1ColorBlockToRgba;
  }
  else if (iVar2 == 0x32545844) {
    *(undefined4 *)((int)this + 0x107c) = 0x10;
    *(code **)((int)this + 0x1084) = CTexture__Helper_00598056;
    *(undefined1 **)((int)this + 0x1080) = &LAB_00598010;
  }
  else if (iVar2 == 0x33545844) {
    *(undefined4 *)((int)this + 0x107c) = 0x10;
    *(code **)((int)this + 0x1084) = CFastVB__PackScalarBlock_4BitEndpoints;
    *(code **)((int)this + 0x1080) = CTexture__Helper_0059778a;
  }
  else if (iVar2 == 0x34545844) {
    *(undefined4 *)((int)this + 0x107c) = 0x10;
    *(code **)((int)this + 0x1084) = CTexture__Helper_0059808a;
    *(undefined1 **)((int)this + 0x1080) = &LAB_00598033;
  }
  else if (iVar2 == 0x35545844) {
    *(undefined4 *)((int)this + 0x107c) = 0x10;
    *(code **)((int)this + 0x1084) = CFastVB__PackScalarBlock_InterpolatedEndpoints;
    *(code **)((int)this + 0x1080) = CTexture__Helper_0059780d;
  }
  puVar4 = (uint *)((int)param_1 + 0x10);
  puVar6 = (uint *)((int)this + 0x1088);
  for (iVar2 = 6; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar6 = *puVar4;
    puVar4 = puVar4 + 1;
    puVar6 = puVar6 + 1;
  }
  *(uint *)((int)this + 0x10a0) = *(uint *)((int)this + 0x1088) & 0xfffffffc;
  *(uint *)((int)this + 0x10a4) = *(uint *)((int)this + 0x108c) & 0xfffffffc;
  *(undefined4 *)((int)this + 0x10b0) = *(undefined4 *)((int)this + 0x1098);
  *(uint *)((int)this + 0x10a8) = *(int *)((int)this + 0x1090) + 3U & 0xfffffffc;
  *(undefined4 *)((int)this + 0x10dc) = 0xffffffff;
  *(undefined4 *)((int)this + 0x10e0) = 0xffffffff;
  *(uint *)((int)this + 0x10ac) = *(int *)((int)this + 0x1094) + 3U & 0xfffffffc;
  *(undefined4 *)((int)this + 0x10b4) = *(undefined4 *)((int)this + 0x109c);
  *(undefined4 *)((int)this + 0x10c8) = *(undefined4 *)((int)this + 0x1048);
  uVar1 = *(int *)((int)this + 0x1040) + 3U & 0xfffffffc;
  uVar5 = *(uint *)((int)this + 0x1038) & 0xfffffffc;
  *(uint *)((int)this + 0x10c0) = uVar1;
  uVar7 = *(uint *)((int)this + 0x103c) & 0xfffffffc;
  uVar3 = *(int *)((int)this + 0x1044) + 3U & 0xfffffffc;
  *(uint *)((int)this + 0x10c4) = uVar3;
  *(uint *)((int)this + 0x10d0) = uVar1 - uVar5 >> 2;
  *(uint *)((int)this + 0x10bc) = uVar7;
  *(int *)((int)this + 0x10cc) = *(int *)((int)this + 0x104c);
  *(uint *)((int)this + 0x10b8) = uVar5;
  *(undefined4 *)((int)this + 0x10e4) = 0;
  *(undefined4 *)((int)this + 0x10e8) = 0;
  *(undefined4 *)((int)this + 0x10ec) = 0;
  *(uint *)((int)this + 0x10d4) = uVar3 - uVar7 >> 2;
  *(int *)((int)this + 0x10d8) = *(int *)((int)this + 0x104c) - *(int *)((int)this + 0x1048);
  return (int)this;
}
