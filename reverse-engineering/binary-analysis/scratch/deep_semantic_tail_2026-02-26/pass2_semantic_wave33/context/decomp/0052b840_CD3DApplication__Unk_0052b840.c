/* address: 0x0052b840 */
/* name: CD3DApplication__Unk_0052b840 */
/* signature: int __fastcall CD3DApplication__Unk_0052b840(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CD3DApplication__Unk_0052b840(void *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  float fVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int unaff_EDI;

  iVar6 = *(int *)((int)param_1 + 0x32e40) * 0x516c;
  iVar2 = *(int *)((int)param_1 + *(int *)((int)param_1 + 0x32e40) * 0x516c + 0x516c);
  iVar5 = iVar2 * 0xf68 + iVar6 + 0x464;
  puVar1 = (undefined4 *)
           ((int)param_1 +
           *(int *)((int)param_1 + iVar2 * 0xf68 + iVar6 + 0x13b4) * 0x18 + iVar5 + 0x140);
  if ((*(int *)((int)param_1 + 0x32e44) == 0) && (*(int *)((int)param_1 + iVar5 + 0x138) == 0)) {
    iVar6 = CD3DApplication__Unk_0052ba50(param_1,(void *)0x1,unaff_EDI);
    return iVar6;
  }
  *(undefined4 *)((int)param_1 + 0x32e4c) = 0;
  uVar7 = (uint)(*(int *)((int)param_1 + 0x32e44) == 0);
  *(uint *)((int)param_1 + 0x32e44) = uVar7;
  *(uint *)((int)param_1 + iVar5 + 0xf54) = uVar7;
  (*(code *)**(undefined4 **)param_1)();
  *(undefined4 *)((int)param_1 + 0x32e78) = *(undefined4 *)((int)param_1 + iVar5 + 0xf54);
  *(undefined4 *)((int)param_1 + 0x32e68) = *(undefined4 *)((int)param_1 + iVar5 + 0xf58);
  *(undefined4 *)((int)param_1 + 0x32e80) = puVar1[5];
  *(undefined4 *)((int)param_1 + 0x32e74) = *(undefined4 *)((int)param_1 + 0x32e94);
  if (*(int *)((int)param_1 + 0x32e44) == 0) {
    *(undefined4 *)((int)param_1 + 0x32e58) = *puVar1;
    *(undefined4 *)((int)param_1 + 0x32e5c) = puVar1[1];
    *(undefined4 *)((int)param_1 + 0x32e60) = puVar1[2];
    *(undefined4 *)((int)param_1 + 0x32e8c) = 1;
  }
  else {
    *(int *)((int)param_1 + 0x32e58) =
         *(int *)((int)param_1 + 0x33014) - *(int *)((int)param_1 + 0x3300c);
    *(int *)((int)param_1 + 0x32e5c) =
         *(int *)((int)param_1 + 0x33018) - *(int *)((int)param_1 + 0x33010);
    uVar3 = *(undefined4 *)((int)param_1 + iVar6 + 0x45c);
    *(undefined4 *)((int)param_1 + 0x32e8c) = 0;
    *(undefined4 *)((int)param_1 + 0x32e60) = uVar3;
  }
  fVar4 = _DAT_005e4aec;
  if ((g_ScreenShape == 1) || (fVar4 = _DAT_005e4af0, g_ScreenShape != 2)) {
    *(float *)((int)param_1 + 0x32e90) =
         ((float)*(uint *)((int)param_1 + 0x32e5c) / (float)*(int *)((int)param_1 + 0x32e58)) *
         fVar4;
  }
  else {
    *(undefined4 *)((int)param_1 + 0x32e90) = 0x3f800000;
  }
  *(uint *)((int)param_1 + 0x32e84) = *(uint *)((int)param_1 + 0x32e84) | 1;
  iVar6 = CD3DApplication__Unk_0052b760(param_1);
  if (iVar6 < 0) {
    if (*(int *)((int)param_1 + 0x32e44) == 0) {
      return -0x7fffbffb;
    }
    iVar6 = CD3DApplication__Unk_0052ba50(param_1,(void *)0x1,unaff_EDI);
    return iVar6;
  }
  if (*(int *)((int)param_1 + 0x32e44) != 0) {
    SetWindowPos(*(HWND *)((int)param_1 + 0x32e94),(HWND)0xfffffffe,*(int *)((int)param_1 + 0x32ffc)
                 ,*(int *)((int)param_1 + 0x33000),
                 *(int *)((int)param_1 + 0x33004) - *(int *)((int)param_1 + 0x32ffc),
                 *(int *)((int)param_1 + 0x33008) - *(int *)((int)param_1 + 0x33000),0x40);
  }
  *(undefined4 *)((int)param_1 + 0x32e4c) = 1;
  return 0;
}
