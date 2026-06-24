/* address: 0x0046a1f0 */
/* name: CUnitAI__GetStringByResolvedTextIdAfter */
/* signature: void __cdecl CUnitAI__GetStringByResolvedTextIdAfter(int param_1, int param_2) */


void __cdecl CUnitAI__GetStringByResolvedTextIdAfter(int param_1,int param_2)

{
  int text_id;

  text_id = CUnitAI__Unk_00469cf0(param_1);
  CText__GetStringByIdAfter(&g_Text,text_id,param_2);
  return;
}
