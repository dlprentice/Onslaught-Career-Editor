/* address: 0x00465f10 */
/* name: CFEPMultiplayerStart__ctor */
/* signature: void * __fastcall CFEPMultiplayerStart__ctor(void * this) */


void * __fastcall CFEPMultiplayerStart__ctor(void *this)

{
  int iVar1;
  void *this_00;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d26d6;
  local_c = ExceptionList;
  ExceptionList = &local_c;
  CMonitor__ctor(this);
  *(undefined ***)this = &PTR_CFrontEndPage__ActiveNotification_NoOp_005d9388;
  local_4 = 0;
  CGenericCamera__ctor_like_00466130((void *)((int)this + 8));
  local_4._0_1_ = 1;
  CDXFrontEndVideo__CDXFrontEndVideo();
  *(undefined4 *)((int)this + 500) = 0xffffffff;
  *(undefined ***)((int)this + 0x278) = &PTR_CFEPMain__Init_005dbae4;
  *(undefined ***)((int)this + 0x29c) = &PTR_LAB_005dbabc;
  *(undefined ***)((int)this + 0x2b0) = &PTR_LAB_005dba68;
  local_4._0_1_ = 2;
  *(undefined ***)((int)this + 700) = &PTR_LAB_005dba94;
  CSPtrSet__ctor((void *)((int)this + 0x2dc));
  *(undefined ***)((int)this + 700) = &PTR_DAT_005dba3c;
  local_4._0_1_ = 3;
  *(undefined ***)((int)this + 0x2ec) = &PTR_LAB_005dba94;
  CSPtrSet__ctor((void *)((int)this + 0x314));
  *(undefined ***)((int)this + 0x2ec) = &PTR_LAB_005dba10;
  *(undefined ***)((int)this + 0x324) = &PTR_LAB_005db9e8;
  local_4._0_1_ = 4;
  *(undefined ***)((int)this + 0x338) = &PTR_CFEPDebriefing__Initialize_005db9c0;
  CFEPLevelSelect__ctor((void *)((int)this + 0x360));
  *(undefined4 *)((int)this + 0x37dc) = &PTR_LAB_005dba94;
  CMissionScriptObjectCode__CMissionScriptObjectCode();
  local_4._0_1_ = 5;
  vector_constructor_iterator_nothrow((void *)((int)this + 0x397c),0x10,3,&LAB_00402d20);
  *(undefined4 *)((int)this + 0x37dc) = &PTR_LAB_005db998;
  *(undefined ***)((int)this + 0x39b8) = &PTR_LAB_005db970;
  *(undefined ***)((int)this + 0x39d0) = &PTR_LAB_005db948;
  local_4 = CONCAT31(local_4._1_3_,6);
  *(undefined ***)((int)this + 0x3c1c) = &PTR_LAB_005db920;
  CFEPMultiplayerStart__SubObj4034__ctor((void *)((int)this + 0x4034));
  *(undefined ***)((int)this + 0x4050) = &PTR_LAB_005db8f8;
  *(undefined ***)((int)this + 0x40b8) = &PTR_CFEPMultiplayerStart__Init_005db8d0;
  *(undefined ***)((int)this + 0x40ec) = &PTR_LAB_005db8a8;
  *(undefined ***)((int)this + 0x4118) = &PTR_CFrontEndPage__Init_ReturnTrue_005db880;
  *(undefined ***)((int)this + 0x4124) = &PTR_CFEPScreenPos__Init_005db858;
  *(undefined ***)((int)this + 0x413c) = &PTR_CFEPVirtualKeyboard__Init_005db830;
  *(undefined ***)((int)this + 0x4834) = &PTR_CFEPDirectory__Init_005db808;
  CFEPMultiplayerStart__SubObj8848__ctor((void *)((int)this + 0x8848));
  *(undefined ***)((int)this + 0xbcc8) = &PTR_CFEPLanguageTest__Init_005db7e0;
  *(undefined ***)((int)this + 0xbde0) = &PTR_CFEPMain__Init_005db7a8;
  *(undefined ***)((int)this + 0xbe04) = &PTR_LAB_005db780;
  *(undefined4 *)((int)this + 0xbe1c) = 1;
  *(undefined4 *)((int)this + 0xbe24) = 0;
  *(undefined4 *)((int)this + 0xbe2c) = 0;
  this_00 = (void *)((int)this + 0xbf40);
  iVar1 = 5;
  do {
    CText__ResetCoreFields(this_00);
    this_00 = (void *)((int)this_00 + 0x30);
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  *(undefined ***)this = &PTR_CFrontEndPage__ActiveNotification_NoOp_005db75c;
  *(undefined1 *)((int)this + 0xbe30) = 0;
  *(undefined4 *)((int)this + 0x274) = 0xffffffff;
  ExceptionList = local_c;
  return this;
}
