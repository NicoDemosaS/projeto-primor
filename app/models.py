from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """Modelo do administrador do sistema"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Garcom(db.Model):
    """Modelo do garçom"""
    __tablename__ = 'garcons'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)  # WhatsApp
    idade = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    pix = db.Column(db.String(100), nullable=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    escalas = db.relationship('Escala', back_populates='garcom', lazy='dynamic')
    
    def __repr__(self):
        return f'<Garcom {self.nome}>'
    
    @property
    def iniciais(self):
        """Retorna as iniciais do nome"""
        partes = self.nome.split()
        if len(partes) >= 2:
            return (partes[0][0] + partes[-1][0]).upper()
        return self.nome[:2].upper()
    
    @property
    def total_eventos(self):
        """Total de eventos que participou"""
        return self.escalas.count()


class Evento(db.Model):
    """Modelo do evento"""
    __tablename__ = 'eventos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)  # Texto livre
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=True)
    local = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    valor_padrao = db.Column(db.Numeric(10, 2), default=0, nullable=False)  # Valor padrão por garçom
    valor_motorista = db.Column(db.Numeric(10, 2), default=0, nullable=False)  # Valor adicional para motorista
    status = db.Column(db.String(20), default='planejado', nullable=False)
    # Status: planejado, notificado, realizado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    escalas = db.relationship('Escala', back_populates='evento', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Evento {self.nome}>'
    
    @property
    def data_formatada(self):
        """Data formatada em pt-BR"""
        return self.data.strftime('%d/%m/%Y')
    
    @property
    def horario(self):
        """Horário formatado"""
        inicio = self.hora_inicio.strftime('%H:%M')
        if self.hora_fim:
            return f"{inicio} - {self.hora_fim.strftime('%H:%M')}"
        return inicio
    
    @property
    def total_garcons(self):
        """Total de garçons escalados"""
        return self.escalas.count()
    
    @property
    def total_confirmados(self):
        """Total de garçons que confirmaram"""
        return self.escalas.filter_by(status='confirmado').count()
    
    @property
    def total_pendentes(self):
        """Total de garçons pendentes"""
        return self.escalas.filter_by(status='pendente').count()
    
    @property
    def total_recusados(self):
        """Total de garçons que recusaram"""
        return self.escalas.filter_by(status='recusado').count()
    
    @property
    def valor_total(self):
        """Valor total do evento (soma dos valores dos garçons + adicional motorista)"""
        total = 0
        for e in self.escalas.all():
            total += float(e.valor)
            if e.is_motorista:
                total += float(self.valor_motorista or 0)
        return total
    
    @property
    def status_badge(self):
        """Retorna classe CSS para o badge de status"""
        badges = {
            'planejado': ('bg-gray-500/20 text-gray-400', 'Planejado'),
            'notificado': ('bg-blue-500/20 text-blue-400', 'Notificado'),
            'realizado': ('bg-green-500/20 text-green-400', 'Realizado'),
        }
        return badges.get(self.status, badges['planejado'])


class Escala(db.Model):
    """Modelo da escala (garçom em evento)"""
    __tablename__ = 'escalas'
    
    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    garcom_id = db.Column(db.Integer, db.ForeignKey('garcons.id'), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    is_motorista = db.Column(db.Boolean, default=False, nullable=False)  # Se é motorista, recebe valor adicional
    status = db.Column(db.String(20), default='pendente', nullable=False)
    # Status: pendente, confirmado, recusado
    token = db.Column(db.String(64), unique=True, nullable=False)
    notificado_em = db.Column(db.DateTime, nullable=True)
    respondido_em = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    evento = db.relationship('Evento', back_populates='escalas')
    garcom = db.relationship('Garcom', back_populates='escalas')
    
    # Índice único para evitar duplicatas
    __table_args__ = (
        db.UniqueConstraint('evento_id', 'garcom_id', name='unique_escala'),
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.token:
            self.token = self.gerar_token()
    
    @staticmethod
    def gerar_token():
        """Gera um token único para confirmação"""
        return secrets.token_urlsafe(32)
    
    def regenerar_token(self):
        """Regenera o token de confirmação"""
        self.token = self.gerar_token()
    
    def __repr__(self):
        return f'<Escala {self.garcom.nome} - {self.evento.nome}>'
    
    @property
    def status_badge(self):
        """Retorna classe CSS e texto para o badge de status"""
        badges = {
            'pendente': ('bg-yellow-500/20 text-yellow-400 border-yellow-500/30', 'Pendente'),
            'confirmado': ('bg-green-500/20 text-green-400 border-green-500/30', 'Confirmado'),
            'recusado': ('bg-red-500/20 text-red-400 border-red-500/30', 'Recusado'),
        }
        return badges.get(self.status, badges['pendente'])
