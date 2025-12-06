import sys
import os
import json

# Ajuste de path para encontrar 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import ai_service

def probar_ia_nivel_dificil():
    print("🔥 Iniciando prueba de estrés a la IA (Nivel Difícil)...")
    print("-------------------------------------------------------")
    
    # TEXTO COMPLEJO:
    # 1. Narrativo (no es una lista).
    # 2. Mezcla tecnologías ("Java", "Spring") dentro de oraciones.
    # 3. Habilidades blandas implícitas ("tuvimos roces", "convencer al cliente").
    # 4. Información basura ("me gusta cocinar", "tengo un perro").
    # 5. Typos leves.
    
    texto_cv_dificil = """
    Resumen:
    Durante los últimos 3 años estuve trabajando en un proyecto de migración legacy para un banco.
    Fue una locura, el código base estaba en Java 7 antiguo y tuvimos que pasarlo todo a una arquitectura
    de microservicios usando Spring Boot y containerizarlo con Docker. 
    
    Al principio el equipo estaba muy desunido, hubo muchas discusiones, así que me tocó asumir el rol de mediador 
    y facilitar la comunicación entre los devs y los de negocio. Logré que se entendieran.
    
    Para la nube, el cliente quería usar AWS, así que implementamos lambdas y S3, aunque yo personalmente
    tengo más experiencia con Azure de mi trabajo anterior.
    
    Datos random: Me gusta salir a correr los domingos y cocinar pasta. Tengo 2 gatos.
    
    En cuanto a bases de datos, soy muy fuerte en PostgreSQL, me encanta optimizar queries lentas, 
    pero en este proyecto nos obligaron a usar MongoDB y tuve que aprenderlo sobre la marcha, ahora lo manejo bien.
    Hablo inglés fluido porque viví un año en Londres.
    """

    print(f"📄 Analizando texto narrativo ({len(texto_cv_dificil)} caracteres)...")

    try:
        resultado = ai_service.extract_skills_from_text(texto_cv_dificil)
        
        print("\n✅ RESPUESTA DE GEMINI:")
        print("-------------------------------------------------------")
        # Imprimimos el JSON bonito
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        print("-------------------------------------------------------")
        
        # Validación visual rápida
        techs = resultado.get("habilidadesTecnicas", [])
        softs = resultado.get("habilidadesBlandas", [])
        
        print(f"\n📊 Análisis rápido:")
        print(f"   - Técnicas detectadas: {len(techs)}")
        print(f"   - Blandas detectadas:  {len(softs)}")
        
        # Desafíos específicos
        if "MongoDB" in techs and "PostgreSQL" in techs:
            print("   ✅ Detectó ambas BDs (la que usó y la que prefiere).")
        if "Cocinar" not in techs and "Cocinar" not in softs:
            print("   ✅ Ignoró correctamente los hobbies (Cocinar).")
        if any("comunicación" in s.lower() or "mediador" in s.lower() for s in softs):
            print("   ✅ Infirió la habilidad blanda del contexto narrativo.")

    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    probar_ia_nivel_dificil()