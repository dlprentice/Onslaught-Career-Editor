/* address: 0x00592c50 */
/* name: CFastVB__ParserContext_Init */
/* signature: void __stdcall CFastVB__ParserContext_Init(void * param_1) */


void CFastVB__ParserContext_Init(void *param_1)

{
  *(code **)param_1 = CFastVB__ParserContext_Shutdown;
  *(undefined1 **)((int)param_1 + 4) = &LAB_00592b40;
  *(undefined4 *)((int)param_1 + 8) = 0x592b20;
  *(undefined1 **)((int)param_1 + 0xc) = &LAB_00592b80;
  *(undefined1 **)((int)param_1 + 0x10) = &LAB_00592c30;
  *(undefined4 *)((int)param_1 + 0x68) = 0;
  *(undefined4 *)((int)param_1 + 0x6c) = 0;
  *(undefined4 *)((int)param_1 + 0x14) = 0;
  *(undefined ***)((int)param_1 + 0x70) = &PTR_s_Bogus_message_code__d_005ed3f8;
  *(undefined4 *)((int)param_1 + 0x74) = 0x7b;
  *(undefined4 *)((int)param_1 + 0x78) = 0;
  *(undefined4 *)((int)param_1 + 0x7c) = 0;
  *(undefined4 *)((int)param_1 + 0x80) = 0;
  return;
}
