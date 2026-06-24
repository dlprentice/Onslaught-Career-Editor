/* address: 0x00521100 */
/* name: CFEPVirtualKeyboard__Render */
/* signature: void __thiscall CFEPVirtualKeyboard__Render(void * this, float transition, int dest) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CFEPVirtualKeyboard__Render(void *this,float transition,int dest)

{
  float fVar1;
  void *pvVar2;
  int iVar3;
  short *psVar4;
  void *unaff_EDI;
  float fVar5;
  int local_8;

  fVar5 = (transition - _DAT_005d85ec) + (transition - _DAT_005d85ec);
  fVar1 = _DAT_005d856c;
  if ((_DAT_005d856c <= fVar5) && (fVar1 = fVar5, _DAT_005d8568 < fVar5)) {
    fVar1 = _DAT_005d8568;
  }
  local_8 = (int)(longlong)ROUND(fVar1 * _DAT_005d8c70);
  if (local_8 < 0) {
    local_8 = 0;
  }
  else if (0xff < local_8) {
    local_8 = 0xff;
  }
  iVar3 = 0xe;
  if (dest != 0xd) {
    iVar3 = dest;
  }
  pvVar2 = (void *)CFEPDirectory__RenderSaveFileList(&DAT_008a1f8c,transition,iVar3);
  if (pvVar2 != (void *)0x0) {
    CUnitAI__Helper_0055eb00((short *)((int)this + 4),pvVar2,0x1f);
    iVar3 = WcsLen((short *)((int)this + 4));
    *(int *)((int)this + 0x44) = iVar3;
    *(undefined1 *)((int)this + 0x48) = 1;
    CFrontEnd__PlaySound(1);
  }
  CFEPMultiplayerStart__Helper_00453140(7.00649e-45,transition);
  CFEPVirtualKeyboard__Helper_00521260(this,DAT_0063fd30,transition,local_8,unaff_EDI);
  fVar5 = transition;
  psVar4 = CFEPSaveGame__Helper_0046a2a0((-(uint)(DAT_008a9580 != 0) & 0xffffffe8) + 0x28);
  CFrontEnd__DrawTitleBar(psVar4,fVar5,(float)dest);
  fVar5 = (transition - _DAT_005d8bc4) * _DAT_005d85bc;
  if (_DAT_005d856c <= fVar5) {
    if (_DAT_005d8568 < fVar5) {
      fVar5 = _DAT_005d8568;
    }
    CFrontEnd__RenderOverlayEffects(fVar5);
    return;
  }
  CFrontEnd__RenderOverlayEffects(_DAT_005d856c);
  return;
}
