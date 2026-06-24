/* address: 0x0057cc8e */
/* name: CFastVB__ClearTripleDword */
/* signature: void __fastcall CFastVB__ClearTripleDword(void * param_1) */


void __fastcall CFastVB__ClearTripleDword(void *param_1)

{
  *(undefined4 *)param_1 = 0;
  *(undefined4 *)((int)param_1 + 4) = 0;
  *(undefined4 *)((int)param_1 + 8) = 0;
  return;
}
